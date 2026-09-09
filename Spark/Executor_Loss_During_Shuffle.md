# Spark Executor Loss During Shuffle

## Error

No final Spark error occurred.

An executor was deliberately terminated while a shuffle workload was running. Spark detected the executor loss, started a replacement executor, retried the required work, and the job completed successfully.

This experiment demonstrates **Spark's recovery mechanism after executor loss during a shuffle**.

---

## Environment

* Spark: 3.5.0
* Master: `local-cluster[2,1,1024]`
* Initial executors: 2
* Executor memory: 512 MB
* Driver memory: 2 GB
* Shuffle partitions: 2
* Docker Desktop
* Jupyter Notebook
* Spark running inside Docker

---

## Reproduction

Created a shuffle workload:

```python
from pyspark.sql import functions as F

slow_df = failure_spark.range(
    0, 100_000_000,
    numPartitions=20
).withColumn(
    "key",
    F.col("id") % 100000
)

slow_result = slow_df.groupBy("key").count()
```

Executed the shuffle:

```python
print("Starting slow shuffle...")
slow_result.count()
print("Shuffle completed")
```

---

## Executor Identification

The Spark application was:

```text
App ID: app-20260904101139-0000
```

Initial executors:

```text
Executor 0 → PID 5242
Executor 1 → PID 5252
```

The processes were identified using:

```powershell
docker exec funny_gould bash -c "ps -ef | grep CoarseGrainedExecutorBackend | grep -v grep"
```

---

## Failure Simulation

Executor 0 was deliberately terminated:

```powershell
docker exec funny_gould bash -c "kill -9 5242"
```

This terminated only the executor process.

The Docker container and Jupyter environment remained running.

---

## Observed Result

Spark detected the executor loss and launched a replacement executor.

Before:

```text
Executor 0 → PID 5242
Executor 1 → PID 5252
```

After:

```text
Executor 1 → PID 5252
Executor 2 → PID 5877
```

The Spark job completed successfully.

---

## Execution Flow

```text
Shuffle workload
      ↓
Executor 0 processing tasks
      ↓
Executor 0 terminated
      ↓
Spark detects executor loss
      ↓
Replacement Executor 2 starts
      ↓
Lost work is retried/recomputed
      ↓
Shuffle completes
      ↓
Job succeeds
```

---

## Why No FetchFailedException Occurred

An executor being lost does not automatically mean the application will fail.

Spark can recover by launching a replacement executor and retrying/recomputing the lost work.

Therefore:

```text
Executor Loss
      ↓
May cause Shuffle Fetch Failure
      ↓
But Spark can sometimes recover automatically
```

In this experiment, Spark successfully recovered.

---

## Root Cause

The executor was intentionally terminated to simulate an executor failure.

In a production environment, executor loss could be caused by:

* Executor OOM
* Kubernetes pod termination
* Node failure
* Container crash
* Network problems
* Disk/resource exhaustion
* Infrastructure failure

---

## Investigation

### Check Spark master

```python
print(failure_spark.sparkContext.master)
```

Result:

```text
local-cluster[2,1,1024]
```

### Confirm shuffle

The physical plan contained:

```text
Exchange hashpartitioning(...)
```

`Exchange` indicates that Spark is performing a shuffle.

### Check executor processes

```powershell
docker exec funny_gould bash -c "ps -ef | grep CoarseGrainedExecutorBackend | grep -v grep"
```

The replacement executor confirmed that Spark recovered from the executor loss.

---

## Final Result

**Executor loss was successfully simulated, but Spark recovered automatically.**

```text
Executor 0 lost
      ↓
Executor replacement
      ↓
Task/work recovery
      ↓
Shuffle completed
      ↓
Application succeeded
```

No `FetchFailedException` was observed.

---

## Lessons Learned

1. Executor loss does not always result in application failure.
2. Spark can automatically replace lost executors in a cluster environment.
3. Lost tasks can be retried and required computation can be regenerated.
4. A shuffle operation contains intermediate data that downstream stages may need to fetch.
5. `FetchFailedException` is a more specific failure where Spark cannot successfully retrieve required shuffle data.
6. Executor loss and shuffle fetch failure should be investigated as related but separate problems.
7. `Exchange` in the physical plan is a useful indicator of a shuffle boundary.
8. Spark UI and executor logs are important when investigating real production shuffle problems.

---

## Related Errors

* `Shuffle_Failure.md`
* `Executor_OOM_Java_Heap.md`
* `OOM_Executor_Lost.md`
* `Driver_OOM_Java_Heap.md`
