# Haystack RAG Helm Chart

A Helm chart for deploying the Haystack Retrieval-Augmented Generation (RAG) stack on Kubernetes.

---

## Testing

The test suite validates:
- All values from values.yaml are respected in the rendered manifests
- Custom values (e.g., replicaCount, resources, env, health checks, ingress) are correctly applied
- Health check and log level configuration is present in deployments
- Ingress and service settings are parameterized

**Sample test case:**

```python
# In tests/run-tests.py

def test_frontend_replica_count(self) -> TestResult:
    """Test that frontend replicaCount is set from values.yaml"""
    print("🧪 Testing frontend replica count...")
    if f"replicas: {self.values['frontend']['replicaCount']}" in self.rendered_yaml:
        return TestResult("Frontend Replica Count", True, "frontend replicaCount is set correctly")
    else:
        return TestResult("Frontend Replica Count", False, "frontend replicaCount is not set correctly")
```

See [`tests/README.md`](./tests/README.md) for full test coverage and instructions.

---

## Installation

```bash
# clone the repo that contains the chart directory
cd haystack-rag

# create secrets override
auth_file=my-values.yaml
cat <<EOF > $auth_file
secret:
  opensearchPassword: <your-opensearch-password>
  openaiApiKey: <your-openai-api-key>
EOF

# install the chart
helm install rag . -n haystack-rag --create-namespace -f $auth_file

# or upgrade
helm upgrade rag . -n haystack-rag -f $auth_file

# open the UI (if using ingress)
xdg-open http://rag.local:8080/
```

> **k3s note:** copy `/etc/rancher/k3s/k3s.yaml` to `~/.kube/config` (or export `KUBECONFIG`) so Helm & kubectl can authenticate.

### Access the UI locally

```bash
sudo -- sh -c 'echo "127.0.0.1 rag.local" >> /etc/hosts'
ssh -L 8080:127.0.0.1:80 <user>@<node-ip> -N &   # tunnel port 80
xdg-open http://rag.local:8080/
```

---

## Health Checks & Verification

After installing or upgrading the chart, Helm will display a dynamic post-install message with health check, access, and troubleshooting instructions. This message is generated from [`templates/NOTES.txt`](./templates/NOTES.txt) and is tailored to your configuration (hostnames, ports, credentials, etc.).

**What NOTES.txt provides:**
- Access URLs for the UI and API, based on your configured hostname and ports
- Example `kubectl` commands for checking pod/service status and logs
- Port-forwarding instructions for local access
- Health check and troubleshooting tips
- Reminders about secrets, DNS, and next steps

To see these instructions at any time, run:

```bash
helm status <release-name> -n <namespace>
```

For more details, see the [NOTES.txt template](./templates/NOTES.txt).

---

## Values reference

The chart is fully parameterized and all major settings are grouped by component. Below is a summary of the most important values. For the full list and defaults, see [`values.yaml`](./values.yaml):

- `namespace`: Namespace to deploy into
- `hostname`: Ingress host header
- `secret.*`: OpenSearch admin password & OpenAI key
- `frontend.*`, `query.*`, `indexing.*`, `opensearch.*`: Per-component settings (replicaCount, port, resources, env, probes, service type, etc.)
- `ingress.*`: Ingress and Traefik middleware settings

See [`values.yaml`](./values.yaml) for all available options and documentation.

---

## Building Images

See [`IMAGES.md`](./IMAGES.md) for instructions on how to build and push the required container images for Kubernetes deployments.

---

## Troubleshooting

| Error | Likely Cause | How to Fix |
|-------|--------------|------------|
|`NameResolutionError: 'opensearch'`| Service missing / mis‑named | `kubectl -n haystack-rag get svc opensearch` |
|Uploads >10 MiB return 413| buffering middleware not attached | check `ingressroute.yaml` annotation & route middlwares |
|`/files` 200 but `/search` 404| `/api` prefix not stripped | ensure `strip-api` middleware is on both API routes |
|Frontend loads but calls `http://localhost:8000/files`| **`REACT_APP_HAYSTACK_API_URL`** was baked incorrectly at **build time** | rebuild frontend image with `--build-arg REACT_APP_HAYSTACK_API_URL=/api` |

---

