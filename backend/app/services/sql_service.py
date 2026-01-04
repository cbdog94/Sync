"""Azure SQL 数据库服务 - KV 存储"""
import datetime
import struct
import threading
from contextlib import contextmanager
from typing import Optional, Dict, List

import pyodbc
from azure.identity import DefaultAzureCredential

from ..config import get_settings


class AzureSqlService:
    """Azure SQL KV 存储服务"""
    
    def __init__(self):
        settings = get_settings()
        self.conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={settings.azure_sql_server};"
            f"DATABASE={settings.azure_sql_database};"
            f"Encrypt=yes;TrustServerCertificate=no;"
        )
        self.credential = DefaultAzureCredential(
            exclude_interactive_browser_credential=False
        )
        self._local = threading.local()
        self._conn_lock = threading.Lock()

    def _create_connection(self) -> pyodbc.Connection:
        """创建新的数据库连接"""
        token_bytes = self.credential.get_token(
            "https://database.windows.net/.default"
        ).token.encode("UTF-16-LE")
        token_struct = struct.pack(
            f"<I{len(token_bytes)}s", len(token_bytes), token_bytes
        )
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        return pyodbc.connect(
            self.conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}
        )

    def _get_connection(self) -> pyodbc.Connection:
        """获取线程本地连接"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = self._create_connection()
        return self._local.conn
    
    def _ensure_connection_valid(self):
        """确保连接有效"""
        try:
            if hasattr(self._local, 'conn') and self._local.conn is not None:
                cursor = self._local.conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
        except Exception:
            self._local.conn = None
            self._local.conn = self._create_connection()
    
    @contextmanager
    def _get_conn(self):
        """连接上下文管理器"""
        self._ensure_connection_valid()
        conn = self._get_connection()
        try:
            yield conn
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            self._local.conn = None
            raise e

    def get(self, key: str) -> Optional[str]:
        """获取单个值"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT v, expiry FROM kv_store WHERE k = ?", key)
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                value, expiry = row
                now = datetime.datetime.now(datetime.timezone.utc)
                if expiry and now > expiry.replace(tzinfo=datetime.timezone.utc):
                    self._delete_with_conn(conn, key)
                    return None
                return value
            return None
    
    def get_many(self, keys: List[str]) -> Dict[str, str]:
        """批量获取多个值"""
        if not keys:
            return {}
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(keys))
            cursor.execute(
                f"SELECT k, v, expiry FROM kv_store WHERE k IN ({placeholders})",
                keys
            )
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
            
            if expired_keys:
                self._delete_many_with_conn(conn, expired_keys)
            
            return result

    def set(self, key: str, value: str, expiry_seconds: int = 3600):
        """设置单个键值对"""
        with self._get_conn() as conn:
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
                key, value, expiry
            )
            conn.commit()
            cursor.close()
    
    def set_many(self, items: Dict[str, str], expiry_seconds: int = 3600):
        """批量设置多个键值对"""
        if not items:
            return
        
        with self._get_conn() as conn:
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
                    key, value, expiry
                )
            conn.commit()
            cursor.close()

    def delete(self, key: str):
        """删除单个键"""
        with self._get_conn() as conn:
            self._delete_with_conn(conn, key)
    
    def delete_many(self, keys: List[str]):
        """批量删除多个键"""
        with self._get_conn() as conn:
            self._delete_many_with_conn(conn, keys)

    def _delete_with_conn(self, conn: pyodbc.Connection, key: str):
        """使用现有连接删除"""
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kv_store WHERE k = ?", key)
        conn.commit()
        cursor.close()
    
    def _delete_many_with_conn(self, conn: pyodbc.Connection, keys: List[str]):
        """使用现有连接批量删除"""
        if not keys:
            return
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(keys))
        cursor.execute(f"DELETE FROM kv_store WHERE k IN ({placeholders})", keys)
        conn.commit()
        cursor.close()


# 单例实例
sql_service = AzureSqlService()
