import os
import datetime
import pyodbc, struct
import threading
from contextlib import contextmanager

from azure.identity import DefaultAzureCredential

# Azure SQL connection settings
server = os.getenv("AZURE_SQL_SERVER")  # e.g., myserver.database.windows.net
database = os.getenv("AZURE_SQL_DATABASE")  # e.g., mydb
driver = "{ODBC Driver 18 for SQL Server}"

if not server or not database:
    print("Please ensure AZURE_SQL_SERVER and AZURE_SQL_DATABASE are set.")
    exit(1)


class AzureSqlClient:
    def __init__(self):
        self.conn_str = (
            f"DRIVER={driver};SERVER={server};DATABASE={database};Encrypt=yes;"
            "TrustServerCertificate=no;"
        )
        # Cache the credential to avoid creating it on every call
        self.credential = DefaultAzureCredential(
            exclude_interactive_browser_credential=False
        )
        # Connection pool (thread-local storage for thread safety)
        self._local = threading.local()
        self._conn_lock = threading.Lock()

    def _create_connection(self):
        """Create a new database connection with authentication token"""
        token_bytes = self.credential.get_token(
            "https://database.windows.net/.default"
        ).token.encode("UTF-16-LE")
        token_struct = struct.pack(
            f"<I{len(token_bytes)}s", len(token_bytes), token_bytes
        )
        SQL_COPT_SS_ACCESS_TOKEN = (
            1256  # This connection option is defined by microsoft in msodbcsql.h
        )
        conn = pyodbc.connect(
            self.conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}
        )
        return conn

    def _get_connection(self):
        """Get thread-local connection, creating if necessary"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            try:
                self._local.conn = self._create_connection()
            except Exception as e:
                print(f"Failed to create connection: {e}")
                raise
        return self._local.conn
    
    def _ensure_connection_valid(self):
        """Ensure the connection is still valid, reconnect if needed"""
        try:
            if hasattr(self._local, 'conn') and self._local.conn is not None:
                # Test connection with a simple query
                cursor = self._local.conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
        except Exception:
            # Connection is dead, recreate it
            self._local.conn = None
            self._local.conn = self._create_connection()
    
    @contextmanager
    def __get_conn(self):
        """Context manager for getting a database connection"""
        self._ensure_connection_valid()
        conn = self._get_connection()
        try:
            yield conn
        except Exception as e:
            # If there's an error, rollback and close connection
            try:
                conn.rollback()
            except:
                pass
            self._local.conn = None
            raise e

    def get(self, key):
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT v, expiry FROM kv_store WHERE k = ?", key)
            row = cursor.fetchone()
            cursor.close()
            if row:
                value, expiry = row
                if expiry and datetime.datetime.now(
                    datetime.timezone.utc
                ) > expiry.replace(tzinfo=datetime.timezone.utc):
                    # Delete expired key in the same connection
                    self._delete_with_conn(conn, key)
                    return None
                return value
            return None
    
    def get_many(self, keys):
        """Batch get operation for multiple keys"""
        if not keys:
            return {}
        
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(keys))
            query = f"SELECT k, v, expiry FROM kv_store WHERE k IN ({placeholders})"
            cursor.execute(query, keys)
            rows = cursor.fetchall()
            cursor.close()
            
            result = {}
            now = datetime.datetime.now(datetime.timezone.utc)
            expired_keys = []
            
            for k, v, expiry in rows:
                if expiry and now > expiry.replace(tzinfo=datetime.timezone.utc):
                    expired_keys.append(k)
                else:
                    result[k] = v
            
            # Delete expired keys in batch
            if expired_keys:
                self._delete_many_with_conn(conn, expired_keys)
            
            return result

    def _delete_with_conn(self, conn, key):
        """Delete using an existing connection (internal method)"""
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kv_store WHERE k = ?", key)
        conn.commit()
        cursor.close()
    
    def _delete_many_with_conn(self, conn, keys):
        """Delete multiple keys using an existing connection"""
        if not keys:
            return
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(keys))
        cursor.execute(f"DELETE FROM kv_store WHERE k IN ({placeholders})", keys)
        conn.commit()
        cursor.close()

    async def delete_expired_keys(self):
        """Clean up expired keys - call periodically, not on every set"""
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM kv_store WHERE expiry IS NOT NULL AND expiry < ?",
                datetime.datetime.now(datetime.timezone.utc),
            )
            conn.commit()
            cursor.close()

    def set(self, key, value, expiry_seconds=3600):
        """Set a single key-value pair (without expensive cleanup)"""
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                seconds=expiry_seconds
            )
            cursor.execute(
                """
                MERGE kv_store AS target
                USING (SELECT ? AS k, ? AS v, ? AS expiry) AS source
                ON target.k = source.k
                WHEN MATCHED THEN
                    UPDATE SET v = source.v, expiry = source.expiry
                WHEN NOT MATCHED THEN
                    INSERT (k, v, expiry) VALUES (source.k, source.v, source.expiry);
            """,
                key,
                value,
                expiry,
            )
            conn.commit()
            cursor.close()
    
    def set_many(self, items, expiry_seconds=3600):
        """Batch set operation for multiple key-value pairs"""
        if not items:
            return
        
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                seconds=expiry_seconds
            )
            
            for key, value in items.items():
                cursor.execute(
                    """
                    MERGE kv_store AS target
                    USING (SELECT ? AS k, ? AS v, ? AS expiry) AS source
                    ON target.k = source.k
                    WHEN MATCHED THEN
                        UPDATE SET v = source.v, expiry = source.expiry
                    WHEN NOT MATCHED THEN
                        INSERT (k, v, expiry) VALUES (source.k, source.v, source.expiry);
                """,
                    key,
                    value,
                    expiry,
                )
            conn.commit()
            cursor.close()

    def delete(self, key):
        with self.__get_conn() as conn:
            self._delete_with_conn(conn, key)
    
    def delete_many(self, keys):
        """Batch delete operation for multiple keys"""
        with self.__get_conn() as conn:
            self._delete_many_with_conn(conn, keys)


# Usage - singleton instance
azure_sql_client = AzureSqlClient()


def get(key):
    return azure_sql_client.get(key)


def get_many(keys):
    """Batch get multiple keys at once"""
    return azure_sql_client.get_many(keys)


def delete(key):
    return azure_sql_client.delete(key)


def delete_many(keys):
    """Batch delete multiple keys at once"""
    return azure_sql_client.delete_many(keys)


def set(key, value):
    azure_sql_client.set(key, value)


def set_many(items, expiry_seconds=3600):
    """Batch set multiple key-value pairs at once"""
    azure_sql_client.set_many(items, expiry_seconds)
