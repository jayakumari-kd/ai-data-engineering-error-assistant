# SQL Server JDBC Connection Refused

## Error

```text
com.microsoft.sqlserver.jdbc.SQLServerException:
The TCP/IP connection to the host localhost, port 9999 has failed.
Error: "Connection refused..."
```

Spark successfully loaded the SQL Server JDBC driver, but the JDBC connection to SQL Server failed.

---

## Environment

* Spark: 3.5.0
* Java: OpenJDK 17.0.8.1
* PySpark running in Jupyter
* Docker Desktop
* Spark container: `funny_gould`
* Spark home: `/usr/local/spark`
* SQL Server JDBC Driver: `mssql-jdbc-13.4.0.jre11.jar`
* JDBC URL used for testing:

```text
jdbc:sqlserver://localhost:9999;databaseName=TestDB
```

---

## Reproduction

Created a test DataFrame:

```python
from pyspark.sql import functions as F

test_df = spark.range(0, 10000).withColumn(
    "name",
    F.concat(F.lit("test_"), F.col("id"))
)

print("Rows:", test_df.count())
```

Result:

```text
Rows: 10000
```

Attempted JDBC write:

```python
jdbc_url = "jdbc:sqlserver://localhost:9999;databaseName=TestDB"

test_df.write \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "dbo.test_table") \
    .option("user", "testuser") \
    .option("password", "testpassword") \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .mode("append") \
    .save()
```

---

## Actual Error

```text
com.microsoft.sqlserver.jdbc.SQLServerException:

The TCP/IP connection to the host localhost, port 9999 has failed.

Error:
"Connection refused. Verify the connection properties.
Make sure that an instance of SQL Server is running on the host
and accepting TCP/IP connections at the port."
```

---

## Root Cause

The JDBC driver was available and loaded successfully.

The failure occurred because no SQL Server service was listening on:

```text
localhost:9999
```

Port `9999` was intentionally selected for this test because it was not hosting SQL Server.

Therefore, the TCP connection was refused.

---

## Important Distinction

This error is different from a missing JDBC driver.

### Missing JDBC driver

```text
ClassNotFoundException:
com.microsoft.sqlserver.jdbc.SQLServerDriver
```

Meaning:

```text
Spark
 ↓
JDBC
 ↓
Driver cannot be loaded
 ↓
Connection never attempted
```

### Connection refused

```text
SQLServerException:
TCP/IP connection ... failed
Connection refused
```

Meaning:

```text
Spark
 ↓
JDBC
 ↓
SQL Server driver loaded
 ↓
Connection attempted
 ↓
Server/port rejected the connection
```

---

## Production Possible Causes

A similar error in a real environment can be caused by:

1. SQL Server service is down.
2. Incorrect SQL Server hostname.
3. Incorrect port.
4. SQL Server is not configured to accept TCP/IP connections.
5. Firewall is blocking the port.
6. Network connectivity/routing issue.
7. Incorrect SQL Server instance configuration.
8. Incorrect JDBC URL.
9. SQL Server is listening on a different port.
10. Container/Kubernetes networking issue.

---

## Investigation

### 1. Verify hostname and port

Confirm the JDBC URL:

```text
jdbc:sqlserver://<SQL_SERVER_HOST>:<PORT>;databaseName=<DATABASE>
```

Do not assume that SQL Server uses the expected port.

---

### 2. Test network connectivity

From the Spark container:

```bash
nc -zv <SQL_SERVER_HOST> <PORT>
```

or:

```bash
curl -v telnet://<SQL_SERVER_HOST>:<PORT>
```

A successful TCP connection indicates that the host/port is reachable.

---

### 3. Check SQL Server

Verify that:

* SQL Server is running.
* TCP/IP is enabled.
* SQL Server is listening on the expected port.
* The expected database exists.

---

### 4. Check firewall/network

Check whether network security rules allow traffic from the Spark environment to the SQL Server host and port.

---

## Fix

For this controlled test, the failure was expected because port `9999` intentionally had no SQL Server listener.

A real fix would be to use the correct reachable SQL Server hostname and port and ensure that SQL Server accepts TCP/IP connections.

Example:

```python
jdbc_url = (
    "jdbc:sqlserver://<SQL_SERVER_HOST>:1433;"
    "databaseName=<DATABASE>"
)
```

Use actual production/test values only in the appropriate secure environment.

---

## Lessons Learned

1. `ClassNotFoundException` and `Connection refused` are different problems.
2. A successfully loaded JDBC driver does not guarantee network connectivity.
3. `Connection refused` generally indicates that the destination host/port was reachable enough to reject the connection, but no service was accepting the connection on that port.
4. Always validate hostname and port before investigating Spark write performance.
5. JDBC troubleshooting should separate:

   * Driver/classpath problems
   * DNS/hostname problems
   * Network connectivity problems
   * SQL Server availability problems
   * Authentication problems
   * Database/table/schema problems
6. Testing with an intentionally invalid port is a safe way to reproduce connection-refused behavior without using a production database.

---

## Related Errors

* `JDBC_Timeout.md`
* `Connection_Reset.md`
* `Spark_Write_Failure_SQLServer.md`
* `Docker/Dockerfile_Not_Found.md`
* `Spark/Executor_OOM_Java_Heap.md`
