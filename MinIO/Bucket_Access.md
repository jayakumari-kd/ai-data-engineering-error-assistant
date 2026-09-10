# MinIO Bucket Access

## Category

MinIO / Bucket / Permissions

## Status

Troubleshooting Reference

---

## Problem

A MinIO alias may be configured successfully while access to a specific bucket or its objects fails.

Typical errors include:

```text
Access Denied
Access Denied to bucket
The specified bucket does not exist
NoSuchBucket
InvalidAccessKeyId
SignatureDoesNotMatch
```

The problem may occur while:

* Listing buckets
* Listing objects
* Reading objects
* Uploading objects
* Downloading objects
* Copying data between buckets
* Backing up MinIO data to S3

---

## Environment

* MinIO Version: `<MINIO_VERSION>`
* `mc` Version: `<MC_VERSION>`
* Environment: `<ENVIRONMENT>`
* MinIO Endpoint: `<MINIO_ENDPOINT>`
* Alias Name: `<ALIAS_NAME>`
* Bucket Name: `<BUCKET_NAME>`
* Authentication Method: Access Key / Secret Key / Service Account

Do not store real access keys, secret keys, internal endpoints, or production bucket names in this document.

---

## What Happened

The MinIO alias was configured successfully, but an operation against a specific bucket or object failed.

A successful alias configuration only confirms that the client can store the alias configuration and, depending on the command/result, may confirm connectivity. It does not guarantee that the authenticated identity has permission to perform every bucket or object operation.

---

## Root Cause

Common causes include:

1. Incorrect bucket name
2. Bucket does not exist
3. Insufficient permissions
4. Incorrect credentials
5. MinIO policy does not allow the required operation
6. Incorrect MinIO endpoint
7. Bucket belongs to a different environment
8. Incorrect object path
9. Credentials were changed, expired, or revoked
10. Signature or authentication configuration mismatch

---

## Investigation

### Step 1 – Verify the Alias

Run:

```bash
mc alias list
```

Confirm:

* Alias name
* MinIO endpoint
* Protocol (`http` / `https`)
* Expected environment

Do not expose credentials in screenshots or documentation.

---

### Step 2 – List Available Buckets

Run:

```bash
mc ls myminio
```

Check whether the required bucket is visible.

If the bucket does not appear, investigate:

* Bucket name
* User permissions
* Environment
* Credentials
* Endpoint

---

### Step 3 – Test Bucket Access

Run:

```bash
mc ls myminio/<BUCKET_NAME>
```

If this returns:

```text
Access Denied
```

investigate the permissions associated with the authenticated identity.

If it returns:

```text
NoSuchBucket
```

verify the bucket name and MinIO environment.

---

### Step 4 – Verify the Object Path

For a specific path:

```bash
mc ls myminio/<BUCKET_NAME>/<PATH>
```

Verify:

* Bucket name
* Prefix/path
* Object name
* Environment

Object paths are case-sensitive.

---

### Step 5 – Check Permissions

Review the policy associated with the MinIO user or service account.

The required permissions depend on the operation.

Examples include:

```text
ListBucket
GetObject
PutObject
DeleteObject
```

Only grant the permissions required by the application or workflow.

---

### Step 6 – Verify Credentials

Authentication errors such as:

```text
InvalidAccessKeyId
SignatureDoesNotMatch
```

can indicate incorrect, expired, revoked, or mismatched credentials.

Verify that the credentials belong to the expected MinIO environment.

Never place actual credentials in the Markdown file.

---

## Resolution

The appropriate resolution depends on the failure identified during investigation.

### Incorrect Bucket Name

Correct the bucket name:

```bash
mc ls myminio/<CORRECT_BUCKET_NAME>
```

### Missing Bucket

Confirm that the bucket exists in the expected environment before attempting to create or access it.

### Insufficient Permissions

Update the relevant MinIO policy to provide only the permissions required for the operation.

For example, a workflow that only reads objects should not automatically receive delete permissions.

### Incorrect Object Path

Correct the bucket or object prefix:

```bash
mc ls myminio/<BUCKET_NAME>/<CORRECT_PATH>
```

### Authentication Problem

Verify the access key, secret key, service account, and target MinIO endpoint.

---

## Validation

After resolving the issue, validate bucket access:

```bash
mc ls myminio/<BUCKET_NAME>
```

Then perform an operation appropriate to the workflow.

### Upload Test

```bash
mc cp <SOURCE_FILE> myminio/<BUCKET_NAME>/
```

### Download Test

```bash
mc cp myminio/<BUCKET_NAME>/<OBJECT> <DESTINATION>
```

Only perform write or delete tests in an appropriate non-production environment unless the operation is explicitly authorized.

---

## Troubleshooting Matrix

| Error                   | Likely Area                             |
| ----------------------- | --------------------------------------- |
| `Access Denied`         | Permissions / Policy                    |
| `NoSuchBucket`          | Bucket name / Environment               |
| `InvalidAccessKeyId`    | Credentials                             |
| `SignatureDoesNotMatch` | Credentials / Endpoint / Authentication |
| `Unable to connect`     | Network / Endpoint                      |
| Object not found        | Bucket / Object path                    |

---

## Important Security Note

Never store real credentials in this error file.

Use placeholders such as:

```text
<ACCESS_KEY>
<SECRET_KEY>
<MINIO_ENDPOINT>
<BUCKET_NAME>
<OBJECT_PATH>
```

Never commit:

* Access keys
* Secret keys
* Tokens
* Passwords
* Internal hostnames
* Production URLs
* Customer-specific bucket names

---

## Lessons Learned

* Successful alias configuration does not guarantee bucket-level access.
* Always verify the bucket name and target environment.
* `Access Denied` should trigger a permission/policy investigation.
* `NoSuchBucket` should trigger a bucket name and environment check.
* Validate both bucket listing and the actual object operation required by the workflow.
* Keep production credentials and internal infrastructure details out of the public knowledge base.

---

## Related Errors

* `Alias_Config.md`
* MinIO Connectivity Issues
* S3 Access / Permission Issues
* Kubernetes Connectivity Issues
* Network / DNS Issues
