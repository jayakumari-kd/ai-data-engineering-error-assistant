# MinIO Bucket Access

## Error Category

MinIO / Bucket / Permissions

## Error Message

Typical errors:

```text
Access Denied
Access Denied to bucket
The specified bucket does not exist
NoSuchBucket
InvalidAccessKeyId
SignatureDoesNotMatch
```

## Environment

* MinIO Version:
* mc Version:
* Environment:
* MinIO Endpoint:
* Alias Name:
* Bucket Name:
* Access Key:
* Authentication Method:

## What Happened

The MinIO alias was configured successfully, but access to a specific bucket or its objects failed.

The issue may occur while:

* Listing buckets
* Listing objects
* Reading objects
* Uploading objects
* Downloading objects
* Copying data between buckets
* Backing up MinIO data to S3

## Root Cause

Common causes:

1. Incorrect bucket name
2. Bucket does not exist
3. Insufficient permissions
4. Incorrect access key or secret key
5. Policy does not allow the required operation
6. Wrong MinIO endpoint
7. Bucket belongs to a different environment
8. Object path is incorrect
9. Credentials were changed or expired

## Investigation

### Step 1 – Verify Alias

```bash
mc alias list
```

Confirm that the correct MinIO endpoint is configured.

### Step 2 – List Buckets

```bash
mc ls myminio
```

Check whether the required bucket exists.

### Step 3 – Check Bucket Access

```bash
mc ls myminio/<bucket-name>
```

If this returns `Access Denied`, investigate permissions.

### Step 4 – Check Object Path

```bash
mc ls myminio/<bucket-name>/<path>
```

Verify that the bucket and object path are correct.

### Step 5 – Check Permissions

Review the policy associated with the MinIO user/service account.

Required permissions depend on the operation.

For example:

```text
ListBucket
GetObject
PutObject
DeleteObject
```

Do not grant more permissions than required.

## Fix Tried

### Attempt 1

Verified bucket name.

**Result:** Corrected an incorrect bucket/path.

### Attempt 2

Verified MinIO alias.

```bash
mc alias list
```

**Result:** Confirmed the correct endpoint.

### Attempt 3

Checked user permissions.

**Result:** Missing bucket permission identified.

### Attempt 4

Updated the required policy.

**Result:** Bucket access restored.

## Final Fix

Example:

```text
The MinIO user had access to the MinIO server but did not have
permission to access the required bucket.

The required bucket permissions were added and access was validated
using mc ls and object read/write tests.
```

## Validation

After fixing the issue, validate:

```bash
mc ls myminio/<bucket-name>
```

Then test an object operation appropriate to the environment:

```bash
mc cp <source> myminio/<bucket-name>/
```

or:

```bash
mc cp myminio/<bucket-name>/<object> <destination>
```

## Important Security Note

Never store real credentials in this error file.

Use placeholders:

```text
<ACCESS_KEY>
<SECRET_KEY>
<MINIO_ENDPOINT>
<BUCKET_NAME>
```

## Lessons Learned

* Successful alias configuration does not guarantee bucket-level access.
* Always verify the bucket name and environment.
* Check permissions when `mc ls` returns `Access Denied`.
* Validate both bucket listing and actual object operations.
* Keep production credentials and internal endpoints out of the knowledge base.

## Related Errors

* Alias_Config.md
* JDBC_Error.md
* Connection_Reset.md
* S3 Access/Permission Issues
