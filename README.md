# AI Data Engineering Error Assistant

A personal AI-powered troubleshooting knowledge base for Data Engineering errors, investigations, reproductions, fixes, and lessons learned.

The project converts practical Data Engineering troubleshooting experience into a structured, searchable Markdown knowledge base and connects it with an AI assistant for troubleshooting guidance.

---

## 🎯 Purpose

Data Engineering troubleshooting knowledge is often scattered across:

* Project incidents
* Tickets
* Logs
* Personal notes
* Configuration changes
* Debugging sessions
* Team discussions
* Memory

This project aims to turn that knowledge into a structured and reusable engineering resource.

The repository captures:

* Real project incidents
* Controlled local reproductions
* Actual error messages and logs
* Root-cause investigations
* Configuration experiments
* Fixes and troubleshooting approaches
* Lessons learned

The knowledge base can be used by AI assistants such as Claude and GitHub Copilot to provide troubleshooting guidance grounded in documented incidents.

---

## 🏗️ Project Workflow

The current workflow is:

```text
Real Data Engineering Error
            ↓
Reproduce / Investigate
            ↓
Capture Error
            ↓
Identify Root Cause
            ↓
Document Incident
            ↓
Markdown Error Library
            ↓
Search Relevant Incidents
            ↓
Claude AI Analysis
            ↓
Streamlit Interface
```

---

## 📚 Library Structure

```text
Data Engineering Error Library/
│
├── README.md
├── PROJECT_CONTEXT.md
├── Dockerfile
├── requirements.txt
├── app.py
├── start_error_assistant.bat
│
├── Notebooks/
│
├── Docker/
│
├── Kubernetes/
│
├── MinIO/
│
├── Spark/
│
└── SQLServer/
```

Each technology area contains Markdown troubleshooting documents.

Example:

```text
Spark/
├── Driver_OOM_Java_Heap.md
├── Executor_OOM_Java_Heap.md
├── OOM_Executor_Lost.md
├── Shuffle_Failure.md
├── Executor_Loss_During_Shuffle.md
└── Spark_Write_Failure_SQLServer.md
```

---

## 🔎 Current Capabilities

The current MVP can:

* Accept a Data Engineering error message
* Search the Markdown error library
* Rank matching incidents using keyword matching
* Display relevant incidents
* Send relevant incident context to Claude
* Generate troubleshooting guidance
* Run through a local Streamlit interface

---

## 🤖 AI Assistant

The application uses Claude to analyze an error together with relevant incidents retrieved from the local knowledge base.

The AI prompt separates:

### Findings from Error Library

Information derived from documented incidents and experiments.

### General Engineering Knowledge

Additional troubleshooting recommendations based on general Data Engineering concepts.

This distinction helps avoid presenting generic AI knowledge as if it were a documented project incident.

---

## 🖥️ Streamlit Interface

The project includes a Streamlit-based interface.

The user can paste an error such as:

```text
java.lang.OutOfMemoryError: Java heap space
```

The application searches the error library and sends the most relevant Markdown incidents to Claude for analysis.

The response can include:

* Likely root cause
* Investigation steps
* Possible fixes
* Relevant documented incidents
* Spark / Kubernetes / SQL tuning considerations
* Confidence level

---

## 🧪 Reproducible Experiments

An important part of this project is reproducing failures locally instead of only documenting theoretical explanations.

Examples include:

### Spark Driver OOM

A controlled experiment demonstrating driver-side Java heap exhaustion during large result collection.

### Spark Executor OOM

A controlled executor-side memory failure demonstrating how executor heap exhaustion differs from driver OOM.

### Executor Loss During Shuffle

A controlled experiment demonstrating executor loss during a shuffle workload and Spark's ability to retry and recompute work.

### SQL Server JDBC Connection Issues

Controlled experiments demonstrating connection-refused and connection-reset scenarios.

These experiments help connect:

```text
Error
   ↓
Failure Mechanism
   ↓
Root Cause
   ↓
Investigation
   ↓
Resolution
```

---

## 🐳 Docker Environment

The project uses Docker to provide a reproducible local development environment containing:

* Jupyter
* PySpark
* Apache Spark
* Python
* Supporting Python packages

This allows experiments and application development to be performed consistently across environments.

---

## 🛠️ Technology Stack

### Data Engineering

* Apache Spark
* PySpark
* SQL
* SQL Server
* JDBC
* Kubernetes
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

### AI / Application

* Claude API
* Python
* Streamlit

### Development

* Docker
* Jupyter
* Git
* GitHub
* VS Code

---

## 🚀 Running the Project Locally

### Prerequisites

Install:

* Docker Desktop
* Git
* VS Code (recommended)

Clone the repository:

```bash
git clone <REPOSITORY_URL>
```

Move into the project directory:

```bash
cd "Data Engineering Error Library"
```

---

## 🔐 Environment Variables

The Claude API key should be supplied through an environment variable.

Example:

```text
ANTHROPIC_API_KEY=<YOUR_API_KEY>
```

Do not commit the actual API key to GitHub.

A future `.env.example` file can be used to document the required environment variables without exposing secrets.

---

## ▶️ Start the Application

The project can be started using the provided startup script:

```text
start_error_assistant.bat
```

Alternatively, Streamlit can be started manually:

```bash
streamlit run app.py
```

The application will be available locally through the Streamlit URL displayed by the command.

---

## 🔒 Security

This repository is intended to contain sanitized, non-confidential troubleshooting knowledge.

Never commit:

* API keys
* Passwords
* Access tokens
* Secret keys
* Internal hostnames
* Internal URLs
* Production credentials
* Customer information
* Confidential logs

Use placeholders such as:

```text
<COMPANY>
<PROD_HOST>
<INTERNAL_URL>
<S3_BUCKET>
<USERNAME>
<TOKEN>
<ACCESS_KEY>
<SECRET_KEY>
```

---

## 🗺️ Roadmap

The project currently uses simple keyword-based search.

Planned improvements:

### Phase 1 — MVP

* Markdown knowledge base
* Keyword search
* Claude integration
* Streamlit interface
* Docker environment

### Phase 2 — Better Search

* Semantic search
* Embeddings
* Improved incident ranking

### Phase 3 — RAG

```text
User Error
    ↓
Semantic Retrieval
    ↓
Relevant Incidents
    ↓
Context Construction
    ↓
Claude
    ↓
Grounded Troubleshooting Response
```

### Phase 4 — Knowledge Platform

Potential future capabilities:

* Error classification
* Automatic incident tagging
* Search filters
* Troubleshooting history
* Error similarity detection
* Team knowledge sharing

---

## 💡 Key Learning

The main learning from this project is that useful AI systems do not always start with complex infrastructure.

A practical progression can be:

```text
Structured
    ↓
Searchable
    ↓
Reproducible
    ↓
Reusable
    ↓
AI-Assisted
    ↓
RAG
```

The long-term goal is to turn operational Data Engineering experience into reusable engineering knowledge.

---

## 👩‍💻 Project Focus

This is a personal learning and knowledge-engineering project focused on combining:

**Data Engineering + Troubleshooting + AI + Reproducibility**

The project intentionally starts simple and evolves toward more advanced retrieval and RAG architecture.
