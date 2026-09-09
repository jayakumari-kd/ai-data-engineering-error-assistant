# Data Engineering Error Library — Project Context

## 1. Project Purpose

This project is a personal Data Engineering troubleshooting and error knowledge library.

The goal is to document real Data Engineering errors, experiments, investigations, root causes, fixes, configurations, and lessons learned in a structured Markdown format.

The library is intended to be used by AI assistants such as Claude or GitHub Copilot so that troubleshooting recommendations are based on my documented incidents and experiments rather than only generic knowledge.

---

## 2. Core Workflow

The intended workflow is:

Real Error / Experiment
        ↓
Reproduce or investigate
        ↓
Capture actual error
        ↓
Identify root cause
        ↓
Document in Markdown
        ↓
Store in Error Library
        ↓
AI searches relevant Markdown files
        ↓
AI provides troubleshooting guidance based on previous incidents

---

## 3. Current Technical Environment

### Local Development

- Operating System: Windows
- Docker Desktop
- VS Code
- Jupyter Notebook
- PySpark
- Spark 3.5.0
- Java 17
- Python
- PowerShell

### Docker Environment

Primary working container:

- Container name: `funny_gould`
- Image: `my-new-image-two`
- Jupyter exposed on port `8888`

The current Spark/Jupyter environment is running inside Docker.

Do not unnecessarily recreate or replace the working container.

---

## 4. Data Engineering Technologies

Primary technologies relevant to this library:

- Apache Spark
- PySpark
- SQL
- SQL Server
- JDBC
- Kubernetes
- Docker
- MinIO
- Amazon S3
- Snowflake
- Hive
- Trino
- Kafka
- Databricks
- Informatica
- AWS
- Azure

Trino documentation is currently deferred and should not be expanded unless specifically requested.

---

## 5. Error Library Structure

Current structure:

```text
Data Engineering Error Library/
│
├── PROJECT_CONTEXT.md
├── README.md
│
├── Notebooks/
│   └── Spark_OOM_Experiments.ipynb
│
├── Docker/
│   ├── Dockerfile_Not_Found.md
│   └── Jupyter_Token_Issue.md
│
├── Kubernetes/
│   ├── CrashLoopBackOff.md
│   └── ImagePullBackOff.md
│
├── MinIO/
│   ├── Alias_Config.md
│   └── Bucket_Access.md
│
├── Spark/
│   ├── Driver_OOM_Java_Heap.md
│   ├── Executor_OOM_Java_Heap.md
│   ├── OOM_Executor_Lost.md
│   ├── Shuffle_Failure.md
│   ├── Executor_Loss_During_Shuffle.md
│   └── Spark_Write_Failure_SQLServer.md
│
└── SQLServer/
    ├── Connection_Reset.md
    ├── JDBC_Connection_Refused.md
    └── JDBC_Timeout.md