# Dockerfile Not Found

## Category

Docker / Dockerfile

## Status

Resolved

## Problem

While building a Docker image, Docker could not find the Dockerfile.

The error was:

```text
open Dockerfile: no such file or directory
```

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

with **no `.txt` extension**.

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

Windows can sometimes hide known file extensions, which makes this problem easy to miss.

## Investigation

### Check the files in the current directory

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

### Check file extensions

In Windows File Explorer:

1. Open the folder containing the Dockerfile.
2. Select **View**.
3. Select **Show**.
4. Enable **File name extensions**.

This makes `.txt`, `.py`, `.md`, etc. visible.

## Resolution

Rename:

```text
Dockerfile.txt
```

to:

```text
Dockerfile
```

Then run the Docker build again.

Example:

```powershell
docker build -t my-data-engineering .
```

The `.` means Docker should use the current directory as the build context.

## Verification

Check that the file exists:

```powershell
Get-ChildItem Dockerfile
```

The output should show:

```text
Dockerfile
```

You can also check:

```powershell
Test-Path .\Dockerfile
```

Expected result:

```text
True
```

## Lessons Learned

* Docker's default build file is named `Dockerfile`.
* `Dockerfile.txt` is a different filename.
* Windows may hide file extensions.
* Always enable **File name extensions** when troubleshooting filename-related Docker errors.
* Use `Get-ChildItem` or `dir` to verify the actual filename.

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

## Related Errors

* Jupyter Token Issue
* Jupyter container startup failure
* Docker image build failure
