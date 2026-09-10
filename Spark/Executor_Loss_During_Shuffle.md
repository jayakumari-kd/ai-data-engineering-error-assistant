# Spark Executor Loss During Shuffle

## Error

No final Spark application error occurred.

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

A shuffle workload was created:

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

The shuffle was then executed:

```python
print("Starting slow shuffle...")

slow_result.count()

print("Shuffle completed")
```

---

## Executor Identification

The Spark application was monitored to identify the executor processes.

The executor processes were identified using a command similar to:

```powershell
docker exec <CONTAINER_NAME> bash -c "ps -ef | grep CoarseGrainedExecutorBackend | grep -v grep"
```

The initial environment contained two executor processes.

> Process IDs and container names are intentionally omitted from this public documentation.

---

## Failure Simulation

One executor process was deliberately terminated to simulate an executor failure.

Example:

```powershell
docker exec <CONTAINER_NAME> bash -c "kill -9 <EXECUTOR_PID>"
```

This terminated only the executor process.

The Docker container and Jupyter environment remained running.

---

## Observed Result

Spark detected the executor loss and launched a replacement executor.

The execution state changed from:

```text
Executor 0
Executor 1
```

to:

```text
Executor 1
Replacement Executor
```

The Spark job completed successfully.

No `FetchFailedException` was observed.

---

## Execution Flow

```text
Shuffle workload
       ↓
Executor processing tasks
       ↓
Executor terminated
       ↓
Spark detects executor loss
       ↓
Replacement executor starts
       ↓
Lost work is retried/recomputed
       ↓
Shuffle completes
       ↓
Job succeeds
```

---

## Why No FetchFailedException Occurred

Executor loss does not automatically mean that the Spark application will fail.

Depending on the stage and the availability of the required shuffle data, Spark may recover by launching a replacement executor and retrying or recomputing lost work.

Therefore:

```text
Executor Loss
       ↓
May cause shuffle-related failure
       ↓
But Spark may recover automatically
```

In this experiment, Spark successfully recovered.

This is an important distinction:

**Executor loss and shuffle fetch failure are related, but they are not the same failure.**

---

## Root Cause

The executor was intentionally terminated to simulate an executor failure.

In a production environment, executor loss could be caused by:

* Executor OOM
* Kubernetes pod termination
* Node failure
* Container crash
* Network problems
* Disk or resource exhaustion
* Infrastructure failure

---

## Investigation

### Check Spark Master

```python
print(failure_spark.sparkContext.master)
```

Expected result:

```text
local-cluster[2,1,1024]
```

### Confirm Shuffle

The physical plan contained:

```text
Exchange hashpartitioning(...)
```

`Exchange` indicates a shuffle boundary in the Spark physical plan.

For example:

```python
slow_result.explain(True)
```

can be used to inspect the physical plan.

### Check Executor Processes

A process-level check can be used to identify executor processes:

```powershell
docker exec <CONTAINER_NAME> bash -c "ps -ef | grep CoarseGrainedExecutorBackend | grep -v grep"
```

The appearance of a replacement executor after the failure confirmed that Spark recovered from the executor loss.

### Check Spark UI

The Spark UI can be used to investigate:

* Failed tasks
* Retried tasks
* Stage execution
* Executor status
* Shuffle read/write
* Task duration
* Executor failures

---

## Final Result

**Executor loss was successfully simulated, and Spark recovered automatically.**

```text
Executor lost
       ↓
Replacement executor
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
2. Spark can replace lost executors in a cluster environment.
3. Lost tasks can be retried and required computation can be regenerated.
4. Shuffle operations create intermediate data that downstream stages may need to fetch.
5. `FetchFailedException` is a more specific failure where Spark cannot successfully retrieve required shuffle data.
6. Executor loss and shuffle fetch failure should be investigated as related but separate problems.
7. `Exchange` in the physical plan is a useful indicator of a shuffle boundary.
8. Spark UI and executor logs are important when investigating production shuffle problems.

---

## Key Learning

A useful troubleshooting distinction is:

```text
Executor Lost
      ≠
FetchFailedException
```

An executor can disappear and the application may still succeed if Spark can recover the required work or shuffle data.

A fetch failure becomes more serious when required shuffle data can no longer be retrieved successfully.

---

## Related Errors

* `Shuffle_Failure.md`
* `Executor_OOM_Java_Heap.md`
* `OOM_Executor_Lost.md`
* `Driver_OOM_Java_Heap.md`

---

## Experiment Status

**Successfully reproduced**

**Executor failure:** Simulated

**Spark recovery:** Successful

**Application failure:** No

**FetchFailedException:** Not observed

**Primary learning:** Executor loss does not necessarily result in shuffle fetch failure or application failure.
