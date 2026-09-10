# SQL Server JDBC Connection Reset

## Error

```text
java.net.SocketException: Connection reset
```

The Spark JDBC connection reached the test endpoint, but the connection was unexpectedly terminated while the JDBC driver was communicating with it.

---

## Environment

* Spark: 3.5.0
* Java: OpenJDK 17
* PySpark running in Jupyter
* Docker Desktop
* Spark running inside Docker
* SQL Server JDBC Driver: `mssql-jdbc-13.4.0.jre11.jar`

No real SQL Server or production credentials were used.

---

## Reproduction

A test DataFrame was created:

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

A controlled fake TCP endpoint was started on port `9997`.

The endpoint accepted the connection and deliberately terminated it.

The JDBC write was then executed:

```python
jdbc_url = "jdbc:sqlserver://localhost:9997;databaseName=TestDB"

test_df.write \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "dbo.test_table") \
    .option("user", "testuser") \
    .option("password", "testpassword") \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .option("loginTimeout", "5") \
    .mode("append") \
    .save()
```

The username and password above were dummy test values.

---

## Actual Error

The important part of the stack trace was:

```text
Caused by: java.net.SocketException: Connection reset

at java.base/sun.nio.ch.NioSocketImpl.implRead(...)
at java.base/java.net.Socket$SocketInputStream.read(...)
at com.microsoft.sqlserver.jdbc.TDSChannel$ProxyInputStream.readInternal(...)
at com.microsoft.sqlserver.jdbc.TDSChannel.read(...)
```

---

## What Happened

The JDBC driver successfully reached the controlled test endpoint.

The connection was then unexpectedly terminated.

```text
Spark
  ↓
JDBC driver
  ↓
TCP connection established
  ↓
Endpoint terminates connection
  ↓
JDBC attempts to read
  ↓
java.net.SocketException
  ↓
Connection reset
```

---

## Root Cause

For this controlled experiment, the connection was deliberately terminated by the fake TCP server.

Therefore, the experiment successfully reproduced a **network-level `Connection reset` condition**.

The experiment did not involve a real SQL Server.

---

## Production Possible Causes

In a real Spark → SQL Server pipeline, possible causes include:

* SQL Server becoming unavailable during the operation
* SQL Server restart
* Network interruption
* Firewall terminating the connection
* Load balancer or proxy closing the connection
* Network device timeout
* Database resource pressure
* Too many concurrent JDBC connections
* Very large or long-running JDBC operations
* Executor or container network problems
* Connection termination while reading or writing data

The exact cause must be determined from the surrounding logs and infrastructure.

---

## Investigation

### 1. Identify Where the Reset Occurred

Check the complete Spark/JDBC stack trace.

Look for:

```text
java.net.SocketException: Connection reset
```

Determine whether the failure occurred during:

* Connection establishment
* Reading data
* Writing data
* Commit
* Result retrieval

---

### 2. Check SQL Server Logs

If the problem occurs in production, check SQL Server logs around the exact failure timestamp.

Look for:

* Server restart
* Connection termination
* Resource pressure
* Network-related errors
* Database availability issues

---

### 3. Check Spark Executor Logs

JDBC writes are commonly executed by Spark executors, so check the executor that reported the failure.

Look for:

```text
Connection reset
SocketException
SQLServerException
Task failed
Executor lost
```

---

### 4. Check Network Infrastructure

Investigate:

* Firewall
* Load balancer
* Proxy
* Network route
* Kubernetes networking
* VPN/private network connectivity

A connection reset does not automatically mean that SQL Server itself caused the problem.

---

### 5. Check JDBC Concurrency

Spark can create multiple JDBC connections when multiple partitions write simultaneously.

For example:

```python
test_df.repartition(10)
```

can result in multiple concurrent JDBC tasks.

Excessive parallelism can put unnecessary connection pressure on SQL Server.

---

## Connection Refused vs Connection Reset

### Connection Refused

```text
Connection refused
```

Usually means the connection could not be established because the target endpoint was not accepting connections.

```text
Spark
  ↓
JDBC
  ↓
❌ Connection refused
```

### Connection Reset

```text
Connection reset
```

Means an established connection was unexpectedly terminated.

```text
Spark
  ↓
JDBC
  ↓
✅ Connection established
  ↓
❌ Connection unexpectedly terminated
```

This distinction is useful when troubleshooting JDBC connectivity problems.

---

## Troubleshooting Checklist

When this occurs in production:

```text
[ ] Check exact failure timestamp
[ ] Identify Spark application
[ ] Identify executor/task that failed
[ ] Check SQL Server availability
[ ] Check SQL Server logs
[ ] Check network/firewall logs
[ ] Check load balancer/proxy
[ ] Check JDBC connection count
[ ] Check Spark partition count
[ ] Check JDBC batch size
[ ] Check whether large data is being written
[ ] Check whether failures are intermittent or consistent
[ ] Investigate before increasing retries
```

---

## Potential Fixes

There is no universal fix for `Connection reset`.

The appropriate action depends on where and why the connection was terminated.

Potential actions include:

* Correct network configuration
* Fix firewall rules
* Resolve SQL Server availability issues
* Reduce excessive JDBC parallelism
* Tune JDBC batch size
* Investigate long-running operations
* Resolve executor/network instability
* Adjust appropriate connection or network timeout settings
* Retry transient failures where appropriate

Avoid blindly increasing timeouts or retries without identifying the underlying cause.

---

## Final Result

**Successfully reproduced a network-level JDBC connection reset.**

The SQL Server JDBC driver was present and loaded successfully.

The connection was established with the controlled test endpoint and then deliberately terminated, producing:

```text
java.net.SocketException: Connection reset
```

---

## Lessons Learned

1. `Connection reset` is different from `Connection refused`.
2. `Connection refused` occurs when the connection cannot be established.
3. `Connection reset` occurs when an established connection is unexpectedly terminated.
4. The reset can originate from SQL Server, the network, firewall, proxy, load balancer, or infrastructure.
5. Spark JDBC writes can create multiple concurrent database connections through partitions.
6. Executor logs are important because JDBC operations are commonly executed by Spark executors.
7. Increasing timeout or retry settings is not always the correct solution.
8. Infrastructure and database logs should be investigated around the failure timestamp.
9. A controlled fake TCP endpoint can reproduce the network-level error without requiring a real SQL Server.

---

## Related Errors

* `JDBC_Connection_Refused.md`
* `JDBC_Timeout.md`
* `Spark_Write_Failure_SQLServer.md`
* `Spark/Executor_OOM_Java_Heap.md`
* `Spark/OOM_Executor_Lost.md`

---

## Experiment Status

**Successfully reproduced**

**Failure:** `java.net.SocketException: Connection reset`

**Test type:** Controlled network simulation

**Real SQL Server used:** No

**Primary learning:** A connection reset indicates that an established connection was unexpectedly terminated; the underlying cause must be investigated across the database, network, and Spark execution layers.
