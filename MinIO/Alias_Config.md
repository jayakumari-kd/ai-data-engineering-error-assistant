# MinIO Alias Configuration

## Error Category

MinIO / mc Client

## Error Message

Typical errors:

```text
mc: Unable to initialize new alias
Access Denied
Invalid Access Key
Invalid Secret Key
Unable to connect to host
```

or

```text
mc: Configuration written to disk, but connection test failed
```

## Environment

* MinIO Version:
* mc Version:
* Environment:
* Endpoint URL:
* Authentication Method:
* Bucket Name:

## What Happened

While configuring a MinIO alias using the `mc` client, the alias creation failed or the alias was created but could not connect to the MinIO server.

This prevented bucket access and object operations.

## Root Cause

Common causes:

1. Incorrect MinIO endpoint URL
2. Wrong access key
3. Wrong secret key
4. SSL/TLS mismatch
5. Network connectivity issue
6. DNS resolution failure
7. Firewall restrictions
8. Expired or rotated credentials

## Investigation

### Step 1 – Verify MinIO Endpoint

Example:

```text
http://minio-host:9000
```

or

```text
https://minio-host:9000
```

### Step 2 – Check Alias Configuration

```bash
mc alias list
```

Verify:

* Alias name
* Endpoint
* Access key
* API type

### Step 3 – Test Connectivity

```bash
ping <minio-host>
```

or

```bash
curl http://<minio-host>:9000/minio/health/live
```

### Step 4 – Validate Credentials

Attempt bucket listing:

```bash
mc ls myminio
```

### Step 5 – Check SSL Settings

For self-signed certificates verify:

```bash
mc alias set myminio https://host:9000 ACCESSKEY SECRETKEY
```

and review certificate trust configuration.

## Fix Tried

### Attempt 1

Verified endpoint URL.

**Result:** Corrected hostname mismatch.

### Attempt 2

Regenerated access credentials.

**Result:** Authentication successful.

### Attempt 3

Verified SSL configuration.

**Result:** Connection established.

### Attempt 4

Validated network path.

**Result:** Firewall issue identified.

## Final Fix

Example:

```text
Alias was configured using an incorrect endpoint URL.
Updated endpoint and verified access credentials.
mc alias configuration succeeded and bucket access was restored.
```

## Configuration

```bash
mc alias set myminio \
http://minio-host:9000 \
ACCESS_KEY \
SECRET_KEY
```

Useful commands:

```bash
mc alias list
mc ls myminio
mc admin info myminio
```

## Lessons Learned

* Verify endpoint URL before checking credentials.
* Always test bucket access after alias creation.
* SSL and certificate issues can appear as connection failures.
* Store credentials securely and rotate when required.

## Related Errors

* Bucket_Access.md
* JDBC_Error.md
* Connection_Reset.md
* MinIO Connectivity Issues
