# Dockerfile Not Found

## Category

Docker / Dockerfile

## Status

Resolved

## Problem

While building a Docker image, Docker could not find the Dockerfile.

Error:

```text
open Dockerfile: no such file or directory
```

---

## What Happened

The Dockerfile had been saved with the filename:

```text
Dockerfile.txt
```

instead of:

```text
Dockerfile
```

Docker expects the default build file to be named exactly:

```text
Dockerfile
```

with no `.txt` extension.

---

## Root Cause

The file extension was incorrect.

Actual filename:

```text
Dockerfile.txt
```

Expected filename:

```text
Dockerfile
```

Windows can sometimes hide known file extensions, making this problem easy to miss.

---

## Investigation

### Check Files in the Current Directory

PowerShell:

```powershell
Get-ChildItem
```

or:

```powershell
dir
```

Check whether the file is named:

```text
Dockerfile
```

or:

```text
Dockerfile.txt
```

### Check File Extensions in Windows

In File Explorer:

1. Open the folder containing the Dockerfile.
2. Select **View**.
3. Select **Show**.
4. Enable **File name extensions**.

This makes extensions such as `.txt`, `.py`, and `.md` visible.

---

## Resolution

Rename:

```text
Dockerfile.txt
```

to:

```text
Dockerfile
```

Then run the Docker build again:

```powershell
docker build -t my-data-engineering .
```

The `.` tells Docker to use the current directory as the build context.

---

## Verification

Check that the Dockerfile exists:

```powershell
Get-ChildItem Dockerfile
```

You can also use:

```powershell
Test-Path .\Dockerfile
```

Expected result:

```text
True
```

---

## Lessons Learned

* Docker's default build file is named `Dockerfile`.
* `Dockerfile.txt` is a different filename.
* Windows may hide known file extensions.
* Enable **File name extensions** when troubleshooting filename-related problems.
* Use `Get-ChildItem` or `dir` to verify the actual filename.

---

## Useful Commands

```powershell
Get-ChildItem
```

```powershell
Test-Path .\Dockerfile
```

```powershell
docker build -t my-data-engineering .
```

---

## Related Errors

* Jupyter Token Issue
* Jupyter container startup failure
* Docker image build failure
