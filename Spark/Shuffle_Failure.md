# Spark Shuffle Failure

## Error Category

Spark

## Error Messages

Typical shuffle-related errors include:

```text
FetchFailedException
MetadataFetchFailedException
ShuffleBlockFetcherIterator
Executor Lost During Shuffle
```

or:

```text
org.apache.spark.shuffle.FetchFailedException
```

---

## Environment

This document describes general shuffle-failure troubleshooting.

Record the following details when documenting a specific incident:

* Spark Version:
* Kubernetes Version:
* Cluster Mode:
* Driver Memory:
* Executor Memory:
* Executor Cores:
* Number of Executors:
* Input Data Size:
* Number of Partitions:

---

## What Happened

A Spark job can fail during a shuffle stage while redistributing data across partitions.

Shuffle operations commonly occur during:

* Join
* Group By
* Order By
* Distinct
* Repartition
* Aggregations

A shuffle failure may occur after tasks have already started processing data.

---

## What Is a Shuffle?

A shuffle occurs when Spark needs to redistribute records across partitions so that related records can be processed together.

For example:

```text
Input Partitions
      ↓
   Shuffle
      ↓
Redistribute by Key
      ↓
Output Partitions
```

In a Spark physical plan, a shuffle is commonly represented by an:

```text
Exchange
```

For example:

```text
Exchange hashpartitioning(key, ...)
```

---

## Root Causes

Common causes of shuffle failures include:

1. Executor OOM during shuffle
2. Data skew causing very large partitions
3. Executor loss or restart
4. Insufficient shuffle partitions
5. Network problems between executors
6. Disk-space exhaustion in `spark.local.dir`
7. Excessive repartitioning
8. Large or expensive joins
9. Shuffle data becoming unavailable after executor loss
10. Infrastructure or container failures

---

## Investigation

### Step 1 – Check Spark UI

Review:

* Failed stage
* Failed tasks
* Shuffle Read Size
* Shuffle Write Size
* Task duration
* Retried tasks
* Skewed tasks
* Executor failures

A single task that processes substantially more data than the others can be an indicator of data skew.

---

### Step 2 – Check Executor Logs

Look for errors such as:

```text
OutOfMemoryError
ExecutorLostFailure
Container killed
Executor exited
Disk error
Connection reset
```

The executor logs can help determine whether the shuffle failure is a symptom of another underlying failure.

---

### Step 3 – Check the Physical Plan

Use:

```python
df.explain(True)
```

Look for:

```text
Exchange
```

An `Exchange` indicates a shuffle boundary in the physical execution plan.

---

### Step 4 – Check Partition Count

Check the current number of partitions:

```python
print(df.rdd.getNumPartitions())
```

Too few partitions can result in very large partitions.

However, simply increasing the number of partitions does not solve every shuffle problem.

---

### Step 5 – Check Data Skew

Identify keys with unusually large record counts.

For example:

```python
from pyspark.sql import functions as F

df.groupBy("key") \
  .count() \
  .orderBy(F.desc("count")) \
  .show(20)
```

A small number of keys containing a very large percentage of the data can create skewed partitions.

---

### Step 6 – Check Shuffle Configuration

Review relevant Spark configuration such as:

```text
spark.sql.shuffle.partitions
spark.default.parallelism
spark.local.dir
```

Also review executor memory and memory overhead when the failure is associated with executor resource exhaustion.

---

## Fixes to Consider

### 1. Increase Executor Memory

If the investigation shows that executors are genuinely running out of memory, increasing executor memory may help.

Example:

```text
spark.executor.memory=4g
```

However, increasing memory should not be used as the only solution when the underlying problem is data skew or an inefficient operation.

---

### 2. Increase Shuffle Partitions

For workloads where partitions are too large, increasing the shuffle partition count may reduce the amount of data handled by each task.

Example:

```python
spark.conf.set(
    "spark.sql.shuffle.partitions",
    "2000"
)
```

The appropriate value depends on workload size, cluster resources, and data distribution.

---

### 3. Repartition Data

For appropriate workloads:

```python
df = df.repartition(1000)
```

Repartitioning can improve distribution before expensive operations such as joins.

However, unnecessary repartitioning creates additional shuffle and can make performance worse.

---

### 4. Address Data Skew

If one or a few keys contain a disproportionate amount of data, increasing executor memory may only mask the problem.

Depending on the workload, possible approaches include:

* Better partitioning
* Salting skewed keys
* Adaptive Query Execution
* Broadcasting an appropriately sized table
* Separating extremely large keys
* Redesigning the aggregation or join

---

### 5. Check `spark.local.dir`

Shuffle data is written to local storage.

Check whether the configured local directories have sufficient:

* Disk space
* I/O capacity
* Permissions

Disk exhaustion can cause shuffle-related failures even when CPU and memory appear healthy.

---

## Important Distinction: Executor Loss vs Fetch Failure

Executor loss and `FetchFailedException` are related but different problems.

An executor can be lost while Spark successfully recovers and recomputes the required work.

For example:

```text
Executor Lost
      ↓
Spark detects failure
      ↓
Replacement executor
      ↓
Lost work recomputed
      ↓
Job succeeds
```

However, if required shuffle data cannot be retrieved successfully, Spark may report a fetch failure:

```text
Executor / Shuffle Data Problem
      ↓
Required shuffle block unavailable
      ↓
Fetch Failure
      ↓
Stage may fail
```

This distinction was demonstrated separately in the **Executor Loss During Shuffle** experiment.

---

## Final Diagnosis

A shuffle failure should not be diagnosed from the `FetchFailedException` message alone.

The investigation should determine **why the shuffle data became unavailable or why the executor failed**.

Possible underlying causes include:

```text
Executor OOM
     OR
Data Skew
     OR
Executor Loss
     OR
Disk Exhaustion
     OR
Network Failure
     OR
Insufficient Partitioning
     ↓
Shuffle Failure
```

---

## Troubleshooting Checklist

When investigating a shuffle failure:

1. Identify the failed stage.
2. Identify the failed task.
3. Check executor logs.
4. Check for executor loss.
5. Check for OOM or container termination.
6. Check shuffle read/write sizes.
7. Check partition sizes.
8. Investigate data skew.
9. Inspect the physical plan for `Exchange`.
10. Review `spark.sql.shuffle.partitions`.
11. Check `spark.local.dir` disk usage.
12. Review network and infrastructure errors.
13. Only then decide whether memory, partitioning, or application logic needs to change.

---

## Lessons Learned

* Large joins and aggregations can generate significant shuffle.
* `FetchFailedException` is usually a symptom of a problem involving shuffle data availability.
* Executor loss does not automatically mean that the Spark application will fail.
* Increasing executor memory alone may not solve a shuffle problem.
* Data skew can create extremely large individual partitions.
* Increasing shuffle partitions can help reduce partition size, but excessive partitioning can introduce additional overhead.
* `Exchange` in the physical plan is a useful indicator of a shuffle boundary.
* Spark UI and executor logs should be reviewed before changing configuration.
* The underlying cause should be identified before applying a tuning change.

---

## Related Errors

* `OOM_Executor_Lost.md`
* `Executor_Loss_During_Shuffle.md`
* `Executor_OOM_Java_Heap.md`
* `Driver_OOM_Java_Heap.md`
* `Kubernetes/CrashLoopBackOff.md`
* `Spark_Write_Failure_SQLServer.md`

---

## Experiment / Documentation Status

**Status:** Troubleshooting reference

**Executor loss experiment:** Documented separately

**FetchFailedException reproduction:** Not confirmed in the documented experiment

**Primary learning:** Shuffle failures should be investigated by identifying the underlying executor, partitioning, disk, network, or data-distribution problem rather than treating `FetchFailedException` as the root cause.
