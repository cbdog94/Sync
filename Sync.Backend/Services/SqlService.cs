using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Options;
using Sync.Backend.Models;

namespace Sync.Backend.Services;

/// <summary>Azure SQL key-value store service</summary>
public class SqlService
{
    private readonly string _connectionString;

    public SqlService(IOptions<SyncSettings> options)
    {
        var settings = options.Value;
        _connectionString = new SqlConnectionStringBuilder
        {
            DataSource = settings.AzureSqlServer,
            InitialCatalog = settings.AzureSqlDatabase,
            Encrypt = true,
            TrustServerCertificate = false,
            Authentication = SqlAuthenticationMethod.ActiveDirectoryDefault,
            ConnectTimeout = 30,
        }.ConnectionString;
    }

    /// <summary>Warm up connection pool (initial connection + AAD token cache)</summary>
    public async Task WarmupAsync()
    {
        await using var conn = await GetConnectionAsync();
    }

    private async Task<SqlConnection> GetConnectionAsync()
    {
        var conn = new SqlConnection(_connectionString);
        await conn.OpenAsync();
        return conn;
    }

    /// <summary>Get a single value by key</summary>
    public async Task<string?> GetAsync(string key)
    {
        await using var conn = await GetConnectionAsync();
        await using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT v, expiry FROM kv_store WHERE k = @k";
        cmd.Parameters.AddWithValue("@k", key);

        await using var reader = await cmd.ExecuteReaderAsync();
        if (!await reader.ReadAsync()) return null;

        var value = reader.GetString(0);
        var expiry = reader.IsDBNull(1) ? (DateTime?)null : reader.GetDateTime(1);

        if (expiry.HasValue && DateTime.UtcNow > expiry.Value)
        {
            await reader.CloseAsync();
            await DeleteInternalAsync(conn, key);
            return null;
        }

        return value;
    }

    /// <summary>Get multiple values by keys</summary>
    public async Task<Dictionary<string, string>> GetManyAsync(IReadOnlyList<string> keys)
    {
        if (keys.Count == 0) return new();

        await using var conn = await GetConnectionAsync();
        await using var cmd = conn.CreateCommand();

        var paramNames = keys.Select((_, i) => $"@k{i}").ToList();
        cmd.CommandText = $"SELECT k, v, expiry FROM kv_store WHERE k IN ({string.Join(",", paramNames)})";
        for (int i = 0; i < keys.Count; i++)
            cmd.Parameters.AddWithValue(paramNames[i], keys[i]);

        var result = new Dictionary<string, string>();
        var expiredKeys = new List<string>();
        var now = DateTime.UtcNow;

        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            var k = reader.GetString(0);
            var v = reader.GetString(1);
            var expiry = reader.IsDBNull(2) ? (DateTime?)null : reader.GetDateTime(2);

            if (expiry.HasValue && now > expiry.Value)
                expiredKeys.Add(k);
            else
                result[k] = v;
        }
        await reader.CloseAsync();

        if (expiredKeys.Count > 0)
            await DeleteManyInternalAsync(conn, expiredKeys);

        return result;
    }

    /// <summary>Set a single key-value pair</summary>
    public async Task SetAsync(string key, string value, int expirySeconds = 3600)
    {
        await using var conn = await GetConnectionAsync();
        await using var cmd = conn.CreateCommand();
        var expiry = DateTime.UtcNow.AddSeconds(expirySeconds);
        cmd.CommandText = @"
            MERGE kv_store AS target
            USING (SELECT @k AS k, @v AS v, @expiry AS expiry) AS source
            ON target.k = source.k
            WHEN MATCHED THEN UPDATE SET v = source.v, expiry = source.expiry
            WHEN NOT MATCHED THEN INSERT (k, v, expiry) VALUES (source.k, source.v, source.expiry);";
        cmd.Parameters.AddWithValue("@k", key);
        cmd.Parameters.AddWithValue("@v", value);
        cmd.Parameters.AddWithValue("@expiry", expiry);
        await cmd.ExecuteNonQueryAsync();
    }

    /// <summary>Set multiple key-value pairs in a transaction</summary>
    public async Task SetManyAsync(Dictionary<string, string> items, int expirySeconds = 3600)
    {
        if (items.Count == 0) return;

        await using var conn = await GetConnectionAsync();
        await using var transaction = conn.BeginTransaction();
        var expiry = DateTime.UtcNow.AddSeconds(expirySeconds);

        try
        {
            foreach (var (key, value) in items)
            {
                await using var cmd = conn.CreateCommand();
                cmd.Transaction = transaction;
                cmd.CommandText = @"
                    MERGE kv_store AS target
                    USING (SELECT @k AS k, @v AS v, @expiry AS expiry) AS source
                    ON target.k = source.k
                    WHEN MATCHED THEN UPDATE SET v = source.v, expiry = source.expiry
                    WHEN NOT MATCHED THEN INSERT (k, v, expiry) VALUES (source.k, source.v, source.expiry);";
                cmd.Parameters.AddWithValue("@k", key);
                cmd.Parameters.AddWithValue("@v", value);
                cmd.Parameters.AddWithValue("@expiry", expiry);
                await cmd.ExecuteNonQueryAsync();
            }
            await transaction.CommitAsync();
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }

    /// <summary>Delete a single key</summary>
    public async Task DeleteAsync(string key)
    {
        await using var conn = await GetConnectionAsync();
        await DeleteInternalAsync(conn, key);
    }

    /// <summary>Delete multiple keys</summary>
    public async Task DeleteManyAsync(IReadOnlyList<string> keys)
    {
        if (keys.Count == 0) return;
        await using var conn = await GetConnectionAsync();
        await DeleteManyInternalAsync(conn, keys);
    }

    private static async Task DeleteInternalAsync(SqlConnection conn, string key)
    {
        await using var cmd = conn.CreateCommand();
        cmd.CommandText = "DELETE FROM kv_store WHERE k = @k";
        cmd.Parameters.AddWithValue("@k", key);
        await cmd.ExecuteNonQueryAsync();
    }

    private static async Task DeleteManyInternalAsync(SqlConnection conn, IReadOnlyList<string> keys)
    {
        await using var cmd = conn.CreateCommand();
        var paramNames = keys.Select((_, i) => $"@k{i}").ToList();
        cmd.CommandText = $"DELETE FROM kv_store WHERE k IN ({string.Join(",", paramNames)})";
        for (int i = 0; i < keys.Count; i++)
            cmd.Parameters.AddWithValue(paramNames[i], keys[i]);
        await cmd.ExecuteNonQueryAsync();
    }
}
