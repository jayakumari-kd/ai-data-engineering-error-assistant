# Data Engineering Error Library — Project Context

## 1. Project Purpose

This project is a personal Data Engineering troubleshooting and error knowledge library.

The goal is to document Data Engineering errors, experiments, investigations, root causes, fixes, configurations, and lessons learned in a structured Markdown format.

The library is intended to support AI assistants such as Claude and GitHub Copilot so that troubleshooting recommendations can be grounded in documented incidents and experiments rather than only generic knowledge.

---

## 2. Core Workflow

The intended workflow is:

```text
Real Error / Experiment
        ↓
Reproduce or Investigate
        ↓
Capture Actual Error
        ↓
Identify Root Cause
        ↓
Document in Markdown
        ↓
Store in Error Library
        ↓
Search Relevant Incidents
        ↓
AI Provides Troubleshooting Guidance
```

---

## 3. Current Technical Environment

### Local Development

* Operating System: Windows
* Docker Desktop
* VS Code
* Jupyter Notebook
* PySpark
* Spark 3.5.0
* Java 17
* Python
* PowerShell

### Docker Environment

The project uses a local Docker-based Spark/Jupyter environment.

* Docker Desktop
* Jupyter
* PySpark
* Spark 3.5.0
* Java 17

The environment is used for local development and reproducible Data Engineering experiments.

---

## 4. Data Engineering Technologies

Primary technologies relevant to this library:

* Apache Spark
* PySpark
* SQL
* SQL Server
* JDBC
* Kubernetes
* Docker
* MinIO
* Amazon S3
* Snowflake
* Hive
* Trino
* Kafka
* Databricks
* Informatica
* AWS
* Azure

Trino documentation is currently deferred.

---

## 5. Error Library Structure

Current structure:

```text
Data Engineering Error Library/
│
├── PROJECT_CONTEXT.md
├── README.md
├── Dockerfile
├── requirements.txt
├── app.py
├── start_error_assistant.bat
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
├── SQLServer/
│   ├── Connection_Reset.md
│   ├── JDBC_Connection_Refused.md
│   └── JDBC_Timeout.md
│
└── Notebooks/
    └── Spark_OOM_Experiments.ipynb
```

---

## 6. Project Architecture

The current MVP follows this general flow:

```text
Data Engineering Error
        ↓
Markdown Error Library
        ↓
Keyword-Based Search
        ↓
Relevant Incident Selection
        ↓
Claude API
        ↓
Troubleshooting Analysis
        ↓
Streamlit UI
```

The project is intentionally designed as a simple local MVP before introducing semantic search, embeddings, vector databases, and RAG.

---

## 7. Security

The project is designed to avoid publishing confidential information.

Sensitive information such as:

* API keys
* Passwords
* Access tokens
* Internal URLs
* Internal hostnames
* Credentials
* Customer information

should never be committed to GitHub.

Secrets are stored locally using environment variables.

---

## 8. Future Improvements

Planned improvements include:

1. Improve error matching
2. Add semantic search
3. Add embeddings
4. Introduce a vector database
5. Implement Retrieval-Augmented Generation (RAG)
6. Improve incident ranking
7. Add richer Streamlit functionality
8. Create a reusable Data Engineering troubleshooting knowledge platform
