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

## Environment

* Spark Version: 3.5.0
* Execution Mode: `local[*]`
* Driver Memory: `1g`
* Environment: Docker + JupyterLab + VS Code
* Container: `my-new-image-two`
* Container remained healthy during the Spark failure

## Reproduction

Spark was started with only 1 GB driver memory:

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

This failed with:

```text
java.lang.OutOfMemoryError: Java heap space
```

## Root Cause

The Spark JVM did not have enough heap memory to handle the data involved in the `collect()` operation.

`collect()` brings the complete result to the driver/Python process instead of keeping the processing distributed.

With only:

```text
spark.driver.memory = 1g
```

the Spark JVM exhausted its Java heap.

## Why `count()` Worked

`count()` only needs to calculate the number of records.

It does not need to transfer the complete dataset into the Python driver.

Therefore:

```text
large_df.count()
```

could complete successfully even though:

```text
large_df.collect()
```

caused driver-side memory exhaustion.

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

These errors were symptoms of the Spark JVM failure, not the original root cause.

## Docker Observation

The Docker container remained healthy:

```text
my-new-image-two
Status: Up (healthy)
```

Therefore:

```text
Docker container → healthy
Jupyter/Python → running
Spark JVM → crashed
```

This is important because a Spark JVM failure does not necessarily mean the entire Docker container has failed.

## Important Classification

This experiment is a **Driver OOM** reproduction.

It is NOT an Executor OOM reproduction.

The reason is that the test used:

```python
.master("local[*]")
```

which runs Spark locally rather than using separate Kubernetes executor processes.

## Lesson

Avoid using:

```python
df.collect()
```

on large datasets.

For large data, prefer distributed operations such as:

```python
df.groupBy(...)
df.write(...)
df.filter(...)
df.select(...)
```

and only collect small results when necessary.

## Production Relevance

In a Kubernetes Spark environment, the same general memory problem can occur at different levels.

Always determine whether the failure is:

1. Driver memory exhaustion
2. Executor memory exhaustion
3. Executor overhead/container memory exhaustion
4. Shuffle-related memory pressure
5. Excessive data returned to the driver

The error message and Spark/Kubernetes logs should be used to distinguish these cases.

## Status

**Successfully reproduced:** Yes

**Failure:** `java.lang.OutOfMemoryError: Java heap space`

**Failure location:** Spark JVM / driver in local mode

**Container failure:** No

**Next experiment:** Reproduce an executor-side memory failure using Spark processes configured to behave more like a distributed environment.
