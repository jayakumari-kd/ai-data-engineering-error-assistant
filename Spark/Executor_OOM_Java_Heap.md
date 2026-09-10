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

* Spark Version: 3.5.0
* Execution Mode: `local-cluster[2,1,1024]`
* Executors: 2
* Cores per executor: 1
* Executor Memory: 512 MB
* Driver Memory: 2 GB
* Environment: Docker + JupyterLab + VS Code
* Java: 17

Spark configuration:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Executor-OOM-Test") \
    .master("local-cluster[2,1,1024]") \
    .config("spark.executor.memory", "512m") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()
```

---

## Reproduction

A large dataset was created:

```python
from pyspark.sql import functions as F

df = spark.range(0, 5_000_000, numPartitions=2)
```

A memory-intensive aggregation was then created:

```python
heavy_df = df.groupBy(
    (F.col("id") % 2).alias("group_id")
).agg(
    F.collect_list(
        F.repeat(F.col("id").cast("string"), 1000)
    ).alias("all_values")
)
```

The following operation succeeded:

```python
heavy_df.count()
```

The aggregated values were then materialized and processed:

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

The most relevant parts of the stack trace were:

```text
UTF8String.repeat
```

followed by:

```text
aggregate.Collect.update
```

This indicates that large strings were being created and accumulated during the aggregation.

---

## Why `count()` Succeeded

This was an important observation during troubleshooting.

The following operation succeeded:

```python
heavy_df.count()
```

Even though the aggregation was memory intensive.

An action such as `count()` does not require the complete aggregated values to be transferred to the Python process.

The later operation:

```python
heavy_df.rdd.map(
    lambda row: len(row.all_values)
).collect()
```

forced the aggregated collection to be materialized and consumed, exposing the executor memory problem.

This demonstrates that the success or failure of a Spark action depends not only on the input size, but also on how the result is materialized and consumed.

---

## Difference From Driver OOM

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

For example:

```python
big_df.count()
```

can successfully process millions of rows.

The problem appeared when the workload required Spark to maintain a large amount of data in memory:

```python
collect_list(...)
```

Therefore, when investigating an OOM, check the **operation, data distribution, and execution plan**, not just the dataset size.

---

## Common Production Causes

Executor OOM can occur because of:

* `collect_list()` / `collect_set()` on large groups
* Large joins
* Data skew
* Very large individual partitions
* Excessive caching or persisting
* Large aggregations
* Large objects created inside UDFs
* Insufficient executor memory
* Insufficient executor memory overhead
* Incorrect partitioning
* Broadcast joins involving unexpectedly large datasets

---

## Troubleshooting Checklist

When an Executor OOM occurs:

1. Determine whether the error originated on the executor or driver.
2. Check the Spark executor logs.
3. Identify the failing stage and task.
4. Check for data skew.
5. Check partition sizes.
6. Look for large `collect_list()` / `collect_set()` operations.
7. Review joins and broadcast operations.
8. Check whether UDFs create large objects.
9. Review executor memory configuration.
10. Review executor memory overhead.
11. Consider whether increasing partition count would reduce per-task memory pressure.
12. Avoid unnecessarily keeping large datasets in executor memory.

---

## Potential Fixes

### Avoid Large `collect_list()`

Instead of collecting millions of values into one group, determine whether the requirement can be satisfied using operations such as:

* `count`
* `sum`
* `min`
* `max`
* `avg`
* Approximate aggregations
* Writing results to storage

The best solution is often to avoid creating an unnecessarily large in-memory collection.

---

### Increase Executor Memory When Appropriate

For example:

```text
spark.executor.memory=4g
```

However, increasing memory should not be the first solution if the underlying operation unnecessarily creates a huge in-memory structure.

---

### Increase Partitioning

For appropriate workloads:

```python
df = df.repartition(20)
```

More partitions can reduce the amount of data processed by an individual task.

However, repartitioning does not automatically solve an aggregation where a single key itself produces an enormous collection.

---

### Investigate Data Skew

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

**Status:** Successfully reproduced in a local Spark cluster.

---

## Lessons Learned

* `local[*]` is useful for reproducing driver-side behavior but does not represent a normal multi-executor cluster.
* `local-cluster` can be useful for reproducing executor-side behavior locally.
* Large datasets do not automatically cause OOM.
* The operation being performed is critical.
* `collect_list()` can create very large in-memory structures.
* Increasing executor memory may mask the symptom without fixing the underlying problem.
* Always distinguish Driver OOM from Executor OOM.
* Data skew can create disproportionately large task-level memory requirements.
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
