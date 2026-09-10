# MinIO Alias Configuration

## Category

MinIO / `mc` Client

## Status

Troubleshooting Reference

---

## Problem

While configuring a MinIO alias using the `mc` client, alias creation may fail or the alias may be created but unable to connect to the MinIO server.

Typical errors include:

```text
mc: Unable to initialize new alias
Access Denied
Invalid Access Key
Invalid Secret Key
Unable to connect to host
```

Another possible message is:

```text
mc: Configuration written to disk, but connection test failed
```

These issues can prevent bucket listing and object operations.

---

## Environment

* MinIO Version: `<MINIO_VERSION>`
* `mc` Version: `<MC_VERSION>`
* Environment: `<ENVIRONMENT>`
* Endpoint URL: `<MINIO_ENDPOINT>`
* Authentication Method: Access Key / Secret Key
* Bucket Name: `<BUCKET_NAME>`

Do not document real credentials, internal hostnames, IP addresses, or customer-specific endpoints in this file.

---

## What Happened

A MinIO alias was configured using the `mc` client.

The alias configuration can fail when the endpoint, credentials, network connectivity, or TLS configuration is incorrect.

An alias being successfully written to the local `mc` configuration does not necessarily mean that the MinIO server is reachable or that the supplied credentials are valid.

---

## Root Cause

Common causes include:

1. Incorrect MinIO endpoint URL
2. Incorrect access key
3. Incorrect secret key
4. HTTP/HTTPS mismatch
5. TLS certificate or trust issue
6. Network connectivity problem
7. DNS resolution failure
8. Firewall or network policy restriction
9. Expired, rotated, or revoked credentials
10. MinIO service unavailable

---

## Investigation

### Step 1 – Verify the MinIO Endpoint

Confirm the correct protocol, hostname, and port.

Example:

```text
http://<MINIO_HOST>:9000
```

or:

```text
https://<MINIO_HOST>:9000
```

Do not assume that port `9000` is correct for every environment.

---

### Step 2 – Check Existing Aliases

Run:

```bash
mc alias list
```

Verify:

* Alias name
* Endpoint
* API configuration
* Whether the expected alias exists

Avoid exposing access keys or other credentials in screenshots or documentation.

---

### Step 3 – Test Network Connectivity

Test whether the MinIO endpoint is reachable.

Example:

```bash
ping <MINIO_HOST>
```

If ICMP is blocked, use an HTTP health check instead:

```bash
curl http://<MINIO_HOST>:9000/minio/health/live
```

For HTTPS:

```bash
curl https://<MINIO_HOST>:9000/minio/health/live
```

A successful network connection does not prove that authentication will succeed.

---

### Step 4 – Validate Credentials

Configure the alias using the appropriate credentials:

```bash
mc alias set myminio \
http://<MINIO_HOST>:9000 \
<ACCESS_KEY> \
<SECRET_KEY>
```

Then test access:

```bash
mc ls myminio
```

If the alias is configured but `mc ls` returns `Access Denied`, investigate credentials and MinIO policies.

---

### Step 5 – Check TLS Configuration

For HTTPS endpoints, verify:

* Certificate validity
* Certificate hostname
* Certificate chain
* Client trust configuration
* HTTP vs HTTPS configuration

Example:

```bash
mc alias set myminio \
https://<MINIO_HOST>:9000 \
<ACCESS_KEY> \
<SECRET_KEY>
```

Do not disable certificate verification as a permanent production fix.

---

### Step 6 – Check MinIO Availability

If administrative access is available:

```bash
mc admin info myminio
```

This can help determine whether the MinIO server is reachable and responding.

---

## Resolution

The appropriate fix depends on the failure observed during investigation.

### Incorrect Endpoint

Correct the hostname, protocol, or port and recreate the alias:

```bash
mc alias set myminio \
http://<MINIO_HOST>:9000 \
<ACCESS_KEY> \
<SECRET_KEY>
```

### Invalid Credentials

Verify that the credentials are:

* Correct
* Active
* Not expired
* Not revoked
* Authorized for the required bucket

Never store credentials directly in Git-tracked files.

### TLS / Certificate Issue

Correct the endpoint protocol and certificate trust configuration.

### Network Issue

Verify:

* DNS resolution
* Network route
* Firewall rules
* Kubernetes network policies, if applicable
* Proxy configuration, if applicable

---

## Verification

After correcting the configuration, verify the alias:

```bash
mc alias list
```

Test bucket access:

```bash
mc ls myminio
```

If administrative access is available:

```bash
mc admin info myminio
```

Successful alias configuration should allow the required MinIO operations without authentication or connectivity errors.

---

## Useful Commands

```bash
mc alias list
```

```bash
mc alias set myminio \
http://<MINIO_HOST>:9000 \
<ACCESS_KEY> \
<SECRET_KEY>
```

```bash
mc ls myminio
```

```bash
mc admin info myminio
```

```bash
curl http://<MINIO_HOST>:9000/minio/health/live
```

---

## Lessons Learned

* Verify the endpoint before troubleshooting credentials.
* Confirm HTTP vs HTTPS configuration.
* Test actual bucket access after creating the alias.
* Separate network, TLS, and authentication failures during investigation.
* Do not publish access keys, secret keys, internal endpoints, or credentials.
* Use environment-specific placeholders when documenting incidents publicly.

---

## Related Errors

* `Bucket_Access.md`
* MinIO Connectivity Issues
* Network / DNS Issues
* TLS / Certificate Issues
* Kubernetes Connectivity Issues
