# Spark Driver OOM - Java Heap Space

## Error

```text
Py4JJavaError: An error occurred while calling o41.collectToPython.

java.lang.OutOfMemoryError: Java heap space
```

Related errors observed:

```text
Py4JNetworkError: Answer from Java side is empty
```

```text
ConnectionRefusedError: [Errno 111] Connection refused
```

---

## Environment

* Spark Version: 3.5.0
* Execution Mode: `local[*]`
* Driver Memory: `1g`
* Environment: Docker + JupyterLab + VS Code
* Java: 17
* Python: 3.x

---

## Reproduction

Spark was started with only 1 GB of driver memory:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("OOM-Reproduction") \
    .master("local[*]") \
    .config("spark.driver.memory", "1g") \
    .getOrCreate()
```

A 10-million-row DataFrame was created:

```python
df = spark.range(0, 10_000_000)
```

A large string column was generated:

```python
large_df = df.selectExpr(
    "id",
    "repeat(cast(id as string), 1000) as large_string"
)
```

The following operation succeeded:

```python
large_df.count()
```

A smaller 1-million-row subset was then collected:

```python
test_df = large_df.limit(1_000_000)

rows = test_df.collect()
```

This resulted in:

```text
java.lang.OutOfMemoryError: Java heap space
```

---

## Root Cause

The Spark driver did not have sufficient memory to handle the large result produced by the `collect()` operation.

`collect()` brings the complete result back to the driver instead of keeping the result distributed across Spark's processing environment.

With:

```text
spark.driver.memory = 1g
```

the Spark driver JVM exhausted its available Java heap while processing the large result.

The subsequent Py4J errors were symptoms of the Spark JVM becoming unavailable.

---

## Why `count()` Worked

`count()` only needs to calculate the number of records.

It does not transfer the complete dataset into the Python process.

Therefore:

```python
large_df.count()
```

could complete successfully even though:

```python
large_df.collect()
```

caused driver-side memory exhaustion.

This demonstrates an important Spark concept:

> A DataFrame can be processed successfully in a distributed manner while collecting the same data to the driver causes memory exhaustion.

---

## Why Py4J Errors Appeared

After the Spark JVM ran out of heap, the Python process could no longer communicate normally with the Java Spark process.

This produced:

```text
Py4JNetworkError:
Answer from Java side is empty
```

and subsequently:

```text
ConnectionRefusedError:
[Errno 111] Connection refused
```

These errors were symptoms of the Spark JVM failure rather than the original root cause.

Therefore, when investigating Py4J communication errors after a Spark action, check the preceding Spark/JVM logs for the actual failure.

---

## Docker Observation

The Docker environment remained healthy during the Spark failure.

The observed state was:

```text
Docker container → healthy
Jupyter/Python → running
Spark JVM → failed
```

This is important because a Spark JVM failure does not necessarily mean that the entire Docker container has failed.

The failure can occur inside the Spark process while the surrounding development environment remains operational.

---

## Important Classification

This experiment is a **Driver OOM** reproduction.

It is **not an Executor OOM** reproduction.

The test used:

```python
.master("local[*]")
```

which runs Spark in local mode rather than using separate distributed executor processes.

Therefore, the memory failure occurred on the Spark driver side.

---

## Investigation Approach

When a Spark job reports an out-of-memory condition, determine where the memory failure occurred before changing configuration.

Useful questions include:

1. Is the application running in local mode or distributed mode?
2. Did the failure occur during `collect()`, `toPandas()`, or another driver-side operation?
3. Did the Spark driver JVM terminate?
4. Did an executor terminate?
5. Are there executor logs showing `OutOfMemoryError`?
6. Is the container being killed because of memory limits?
7. Is excessive data being returned to the driver?
8. Is a large aggregation or shuffle causing memory pressure?

This prevents incorrectly increasing executor memory when the actual problem is driver-side data collection.

---

## Recommended Approach

Avoid using:

```python
df.collect()
```

on large datasets.

For large datasets, prefer distributed operations such as:

```python
df.filter(...)
df.select(...)
df.groupBy(...)
df.write(...)
```

Only collect small result sets when necessary.

For example:

```python
small_result = df.limit(100).collect()
```

can be appropriate when the result is known to be small.

---

## Production Relevance

In a Kubernetes or other distributed Spark environment, memory problems can occur at different levels.

Always determine whether the failure is related to:

1. Driver memory exhaustion
2. Executor memory exhaustion
3. Executor memory overhead
4. Container memory limits
5. Shuffle-related memory pressure
6. Excessive data returned to the driver
7. Large aggregations
8. Data skew

The error message, Spark UI, application logs, executor logs, and Kubernetes/container status should be used together to identify the failure location.

---

## Key Learning

The most important lesson from this experiment is:

```text
Distributed processing ≠ collecting distributed data
```

Spark can process a large dataset successfully while a subsequent `collect()` causes driver memory exhaustion.

The operation being performed is therefore just as important as the dataset size when diagnosing Spark memory problems.

---

## Status

**Successfully reproduced:** Yes

**Failure:** `java.lang.OutOfMemoryError: Java heap space`

**Failure location:** Spark driver JVM in local mode

**Container failure:** No

**Root cause:** Insufficient driver-side memory while processing a large collected result

**Next experiment:** Reproduce an executor-side memory failure using Spark processes configured to behave more like a distributed environment.
