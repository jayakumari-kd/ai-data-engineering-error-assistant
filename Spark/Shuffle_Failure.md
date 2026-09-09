# Shuffle Failure

## Error Category

Spark

## Error Message

Typical errors:

```text
FetchFailedException
MetadataFetchFailedException
ShuffleBlockFetcherIterator
Executor Lost During Shuffle
```

or

```text
org.apache.spark.shuffle.FetchFailedException
```

## Environment

* Spark Version:
* Kubernetes Version:
* Cluster Mode:
* Driver Memory:
* Executor Memory:
* Executor Cores:
* Number of Executors:
* Input Data Size:
* Number of Partitions:

## What Happened

A Spark job failed during a shuffle stage while redistributing data across executors for operations such as:

* Join
* Group By
* Order By
* Distinct
* Repartition

The failure occurred after tasks had already started processing data.

## Root Cause

Possible causes:

1. Executor OOM during shuffle
2. Data skew causing a few partitions to become extremely large
3. Executor lost or restarted
4. Insufficient shuffle partitions
5. Network issues between executors
6. Disk space exhaustion in spark.local.dir
7. Excessive repartitioning

## Investigation

### Step 1 – Check Spark UI

Review:

* Failed Stage
* Failed Tasks
* Shuffle Read Size
* Shuffle Write Size
* Skewed Tasks

### Step 2 – Check Executor Logs

Look for:

```text
OutOfMemoryError
Container killed by YARN/Kubernetes
Executor Lost
```

### Step 3 – Check Partition Count

```python
print(df.rdd.getNumPartitions())
```

### Step 4 – Check Data Skew

Identify keys with very large record counts.

### Step 5 – Check Shuffle Configuration

```text
spark.sql.shuffle.partitions
spark.default.parallelism
spark.local.dir
```

## Fix Tried

### Attempt 1

Increased executor memory.

**Result:** Partial improvement but issue returned.

### Attempt 2

Increased shuffle partitions.

Example:

```python
spark.conf.set("spark.sql.shuffle.partitions", "2000")
```

**Result:** Reduced partition size.

### Attempt 3

Repartitioned data before join.

```python
df = df.repartition(1000)
```

**Result:** Improved distribution.

## Final Fix

Document the actual fix used in production.

Example:

```text
Root cause was data skew on a single join key.
Applied repartitioning and increased shuffle partitions.
Job completed successfully.
```

## Configuration

```text
spark.sql.shuffle.partitions=
spark.default.parallelism=
spark.executor.memory=
spark.executor.cores=
spark.local.dir=
```

## Lessons Learned

* Large joins generate heavy shuffle.
* Increasing memory alone may not solve shuffle failures.
* Always check for skewed partitions.
* Review Spark UI before changing configuration.

## Related Errors

* OOM_Executor_Lost.md
* Spark_Write_Failure_SQLServer.md
* Kubernetes OOMKilled

```

After this, I'd create **`Trino/Driver_Mismatch.md`** next because you've already experienced a Trino JDBC driver version issue.
```
