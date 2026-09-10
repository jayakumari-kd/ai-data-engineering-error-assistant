# SQL Server JDBC Connection Refused

## Error

```text id="c0d9f1"
com.microsoft.sqlserver.jdbc.SQLServerException:

The TCP/IP connection to the host localhost, port 9999 has failed.

Error: "Connection refused..."
```

Spark successfully loaded the SQL Server JDBC driver, but the JDBC connection to the test endpoint failed.

---

## Environment

* Spark: 3.5.0
* Java: OpenJDK 17
* PySpark running in Jupyter
* Docker Desktop
* Spark running inside Docker
* SQL Server JDBC Driver: `mssql-jdbc-13.4.0.jre11.jar`

Test JDBC URL:

```text id="5g1l0a"
jdbc:sqlserver://localhost:9999;databaseName=TestDB
```

No real SQL Server or production credentials were used.

---

## Reproduction

A test DataFrame was created:

```python id="y43s4h"
from pyspark.sql import functions as F

test_df = spark.range(0, 10000).withColumn(
    "name",
    F.concat(F.lit("test_"), F.col("id"))
)

print("Rows:", test_df.count())
```

Result:

```text id="h6x9z8"
Rows: 10000
```

A JDBC write was then attempted:

```python id="r4b5n0"
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

The username and password above were dummy test values.

---

## Actual Error

```text id="r5e8q2"
com.microsoft.sqlserver.jdbc.SQLServerException:

The TCP/IP connection to the host localhost, port 9999 has failed.

Error:

"Connection refused. Verify the connection properties.

Make sure that an instance of SQL Server is running on the host
and accepting TCP/IP connections at the port."
```

---

## Root Cause

The SQL Server JDBC driver was available and loaded successfully.

The failure occurred because no SQL Server service was listening on the test endpoint:

```text id="2k5n3q"
localhost:9999
```

Port `9999` was intentionally selected for this controlled test.

Therefore, the connection attempt resulted in:

```text id="h0q1e6"
Connection refused
```

---

## Important Distinction

This error is different from a missing JDBC driver.

### Missing JDBC Driver

```text id="m7x8p4"
ClassNotFoundException:
com.microsoft.sqlserver.jdbc.SQLServerDriver
```

Meaning:

```text id="3f5k7a"
Spark
  ↓
JDBC
  ↓
Driver cannot be loaded
  ↓
Connection cannot be attempted
```

### Connection Refused

```text id="n2p8w6"
SQLServerException:
TCP/IP connection ... failed
Connection refused
```

Meaning:

```text id="q6c4v1"
Spark
  ↓
JDBC
  ↓
SQL Server driver loaded
  ↓
Connection attempted
  ↓
Target endpoint refused the connection
```

This helps distinguish a **classpath/driver problem** from a **connectivity or service-availability problem**.

---

## Production Possible Causes

A similar error in a real environment can be caused by:

1. SQL Server service being down
2. Incorrect SQL Server hostname
3. Incorrect port
4. SQL Server not configured to accept TCP/IP connections
5. Firewall or network security rules blocking the connection
6. Network routing or connectivity problems
7. Incorrect SQL Server instance configuration
8. Incorrect JDBC URL
9. SQL Server listening on a different port
10. Container or Kubernetes networking issues

---

## Investigation

### 1. Verify Hostname and Port

Confirm the JDBC URL:

```text id="n3p7q5"
jdbc:sqlserver://<SQL_SERVER_HOST>:<PORT>;databaseName=<DATABASE>
```

Do not assume that SQL Server uses a particular port.

---

### 2. Test TCP Connectivity

From the Spark environment, test whether the target host and port are reachable.

For example:

```bash id="u7z5e3"
nc -zv <SQL_SERVER_HOST> <PORT>
```

Another option is:

```bash id="q8w4k2"
curl -v telnet://<SQL_SERVER_HOST>:<PORT>
```

These tests check basic TCP connectivity and can help separate network problems from JDBC-specific problems.

---

### 3. Check SQL Server

Verify that:

* SQL Server is running
* TCP/IP is enabled
* SQL Server is listening on the expected port
* The expected database exists

---

### 4. Check Firewall and Network

Verify that network security rules allow traffic from the Spark environment to the SQL Server host and port.

For Kubernetes or containerized environments, also verify the relevant network routes and policies.

---

## Fix

For this controlled test, the failure was expected because port `9999` intentionally had no SQL Server listener.

In a real environment, the appropriate fix would be to use the correct reachable SQL Server hostname and port and ensure that SQL Server accepts TCP/IP connections.

Example:

```python id="d1k8r6"
jdbc_url = (
    "jdbc:sqlserver://<SQL_SERVER_HOST>:1433;"
    "databaseName=<DATABASE>"
)
```

Use actual environment-specific values only in the appropriate secure environment.

---

## Troubleshooting Checklist

```text id="z5r2m9"
[ ] Verify JDBC driver is available
[ ] Verify JDBC URL
[ ] Verify hostname
[ ] Verify port
[ ] Test TCP connectivity
[ ] Check SQL Server availability
[ ] Check TCP/IP configuration
[ ] Check firewall/network rules
[ ] Check container/Kubernetes networking
[ ] Check database availability
[ ] Check authentication after connectivity is confirmed
```

---

## Lessons Learned

1. `ClassNotFoundException` and `Connection refused` are different problems.
2. A successfully loaded JDBC driver does not guarantee network connectivity.
3. `Connection refused` generally indicates that the connection attempt reached the target networking layer but the target endpoint did not accept the connection.
4. Always validate hostname and port before investigating Spark JDBC write performance.
5. JDBC troubleshooting should separate:

   * Driver/classpath problems
   * DNS/hostname problems
   * Network connectivity problems
   * SQL Server availability problems
   * Authentication problems
   * Database/table/schema problems
6. Testing with an intentionally unused port is a safe way to reproduce connection-refused behavior without using a production database.

---

## Final Result

**Successfully reproduced JDBC connection-refused behavior.**

The SQL Server JDBC driver was available and loaded successfully.

The connection attempt to the intentionally unused test port failed with:

```text id="j1v5c8"
Connection refused
```

This confirmed that the experiment reproduced a **connectivity/service-availability failure**, rather than a JDBC driver loading problem.

---

## Related Errors

* `Connection_Reset.md`
* `JDBC_Timeout.md`
* `Spark_Write_Failure_SQLServer.md`
* `Docker/Dockerfile_Not_Found.md`
* `Spark/Executor_OOM_Java_Heap.md`

---

## Experiment Status

**Successfully reproduced**

**Failure:** TCP connection refused

**Real SQL Server used:** No

**Primary learning:** A loaded JDBC driver and a reachable/available SQL Server are separate concerns. Validate the driver, hostname, port, network connectivity, and database availability independently.
