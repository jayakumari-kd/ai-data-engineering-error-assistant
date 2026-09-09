# Spark Executor OOM - Java Heap Space

## Error

```text
java.lang.OutOfMemoryError: Java heap space
    at org.apache.spark.unsafe.types.UTF8String.repeat(UTF8String.java:735)
    at org.apache.spark.sql.catalyst.expressions.BinaryExpression.eval(Expression.scala:672)
    at org.apache.spark.sql.catalyst.expressions.aggregate.Collect.update(collect.scala:53)
```

The failure occurred while executing a Spark aggregation using `collect_list()`.

---

## Environment

* Spark version: 3.5.0
* Mode: `local-cluster[2,1,1024]`
* Executors: 2
* Cores per executor: 1
* Executor memory: 512 MB
* Driver memory: 2 GB
* Running inside Docker + JupyterLab + VS Code
* Docker container remained healthy

Spark configuration:

```python
spark = SparkSession.builder \
    .appName("Executor-OOM-Test") \
    .master("local-cluster[2,1,1024]") \
    .config("spark.executor.memory", "512m") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()
```

---

## Reproduction

First, a large dataset was created:

```python
from pyspark.sql import functions as F

df = spark.range(0, 5_000_000, numPartitions=2)
```

A memory-heavy aggregation was then created:

```python
heavy_df = df.groupBy(
    (F.col("id") % 2).alias("group_id")
).agg(
    F.collect_list(
        F.repeat(F.col("id").cast("string"), 1000)
    ).alias("all_values")
)
```

Calling:

```python
heavy_df.count()
```

succeeded.

To force the aggregated values to be materialized and processed:

```python
result = heavy_df.rdd.map(
    lambda row: len(row.all_values)
).collect()

print(result)
```

This resulted in:

```text
java.lang.OutOfMemoryError: Java heap space
```

---

## Root Cause

The executor ran out of Java heap memory while building the large `collect_list()` aggregation.

Each input row was converted into a large string using:

```python
F.repeat(F.col("id").cast("string"), 1000)
```

Millions of these values were then accumulated into an in-memory collection:

```python
collect_list(...)
```

This caused the executor to require more heap memory than the configured 512 MB.

The important part of the stack trace was:

```text
UTF8String.repeat
```

followed by:

```text
aggregate.Collect.update
```

This indicates that the large strings were being created and accumulated during the aggregation.

---

## Why `count()` Succeeded

This was an important observation during troubleshooting.

The following succeeded:

```python
heavy_df.count()
```

Even though the aggregation was memory intensive.

An action such as `count()` does not necessarily require all of the large output values to be transferred to the driver or fully consumed in Python.

The later operation:

```python
heavy_df.rdd.map(
    lambda row: len(row.all_values)
).collect()
```

forced the aggregated collection to be materialized and processed, exposing the executor memory problem.

---

## Difference From Driver OOM Experiment

### Driver OOM

Previous experiment:

```text
Master: local[*]
Driver memory: 1 GB
Large rows
        ↓
collect()
        ↓
Driver JVM heap exhausted
```

Observed:

```text
java.lang.OutOfMemoryError: Java heap space
Py4JNetworkError: Answer from Java side is empty
ConnectionRefusedError
```

Classification:

**Driver OOM**

---

### Executor OOM

Current experiment:

```text
Master: local-cluster[2,1,1024]
Executor memory: 512 MB
        ↓
Large strings
        ↓
collect_list()
        ↓
Executor aggregation memory exhausted
```

Observed:

```text
java.lang.OutOfMemoryError: Java heap space
```

Classification:

**Executor OOM**

---

## Key Investigation Lesson

Large input size alone does not necessarily cause an Executor OOM.

For example, processing millions of rows with:

```python
big_df.count()
```

successfully completed.

The problem appeared when the workload required Spark to maintain a large amount of data in memory:

```python
collect_list(...)
```

Therefore, when investigating an OOM, check the **operation and execution plan**, not just the dataset size.

---

## Common Production Causes

Executor OOM can occur because of:

* `collect_list()` / `collect_set()` on large groups
* Large joins
* Data skew
* Very large individual partitions
* Excessive caching/persisting
* Large aggregations
* Large objects created inside UDFs
* Insufficient executor memory
* Insufficient executor memory overhead
* Incorrect partitioning
* Broadcast joins involving unexpectedly large datasets

---

## Troubleshooting Checklist

When an Executor OOM occurs:

1. Check whether the error is coming from the executor or driver.
2. Look at the Spark executor logs.
3. Check the failing stage and task.
4. Check for data skew.
5. Check partition sizes.
6. Look for large `collect_list()` / `collect_set()` operations.
7. Review joins and broadcast operations.
8. Check whether large objects are being created by UDFs.
9. Review executor memory configuration.
10. Review executor memory overhead.
11. Consider increasing partition count.
12. Avoid unnecessarily keeping large datasets in executor memory.

---

## Potential Fixes

### Avoid large `collect_list()`

Instead of collecting millions of values into one group, consider whether the business requirement can be satisfied with:

* `count`
* `sum`
* `min`
* `max`
* `avg`
* approximate aggregations
* writing results to storage

---

### Increase executor memory when appropriate

Example:

```text
spark.executor.memory=4g
```

However, increasing memory should not be the first solution if the underlying operation unnecessarily creates huge in-memory structures.

---

### Increase partitioning

For appropriate workloads:

```python
df = df.repartition(20)
```

More partitions can reduce the amount of data processed by an individual task.

However, repartitioning does not automatically fix an aggregation where one key itself produces an enormous collection.

---

### Investigate data skew

If one group contains most of the records, a single task may receive disproportionately large amounts of data.

Check the distribution of keys before assuming that simply increasing executor memory will solve the problem.

---

## Final Diagnosis

**Error Type:** Executor OOM

**Primary Cause:** Large in-memory `collect_list()` aggregation combined with large string values.

**Evidence:**

```text
java.lang.OutOfMemoryError: Java heap space
```

and:

```text
UTF8String.repeat
```

```text
aggregate.Collect.update
```

**Status:** Successfully reproduced in the local Spark cluster.

---

## Lessons Learned

* `local[*]` is useful for reproducing Driver-side problems but does not represent a normal multi-executor cluster.
* `local-cluster` can be used to reproduce executor-side behavior locally.
* Large datasets do not automatically mean OOM.
* The operation being performed is critical.
* `collect_list()` can create very large in-memory structures.
* Increasing executor memory may mask the symptom without fixing the underlying problem.
* Always distinguish Driver OOM from Executor OOM.
* `Py4JNetworkError` can be a secondary symptom when the Spark JVM has already died; the underlying Java exception should be investigated first.

---

## Related Errors

* `Spark/OOM_Executor_Lost.md`
* `Spark/Driver_OOM_Java_Heap.md`
* `Spark/Shuffle_Failure.md`
* `Kubernetes/CrashLoopBackOff.md`

---

## Experiment Status

**Successfully reproduced.**

Environment:

```text
Spark 3.5.0
local-cluster[2,1,1024]
Executor memory: 512 MB
Driver memory: 2 GB
```
