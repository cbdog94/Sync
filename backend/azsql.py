import os
import datetime
import pyodbc, struct

from azure.identity import DefaultAzureCredential
import asyncio

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

    def __get_conn(self):
        credential = DefaultAzureCredential(
            exclude_interactive_browser_credential=False
        )
        token_bytes = credential.get_token(
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

    def get(self, key):
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT v, expiry FROM kv_store WHERE k = ?", key)
            row = cursor.fetchone()
            if row:
                value, expiry = row
                if expiry and datetime.datetime.now(
                    datetime.timezone.utc
                ) > expiry.replace(tzinfo=datetime.timezone.utc):
                    self.delete(key)
                    return None
                return value
            return None

    async def delete_expired_keys(self):
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM kv_store WHERE expiry IS NOT NULL AND expiry < ?",
                datetime.datetime.now(datetime.timezone.utc),
            )
            conn.commit()

    def set(self, key, value, expiry_seconds=3600):
        # Call delete_expired_keys logic
        asyncio.run(self.delete_expired_keys())

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

    def delete(self, key):
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kv_store WHERE k = ?", key)
            conn.commit()


# Usage
azure_sql_client = AzureSqlClient()


def get(key):
    return azure_sql_client.get(key)


def delete(key):
    return azure_sql_client.delete(key)


def set(key, value):
    azure_sql_client.set(key, value)
