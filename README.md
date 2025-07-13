# Haystack‑RAG Helm Chart

> Helm chart to deploy the full **[Haystack RAG demo](https://github.com/deepset-ai/haystack-rag-app)**—OpenSearch, indexing worker, query API and a React UI—onto any Kubernetes ≥ 1.25 cluster.  The manifests are tuned for k3s/k3d but run on vanilla clusters as well.

---

## Tested matrix

| Dependency | Version(s) | Notes |
|------------|------------|-------|
| Kubernetes | 1.25 – 1.29 | k3s 1.29.x, k3d, KinD, EKS 1.28 tested |
| Helm       | v3.14.3    | use any 3.x, but strict‑lint flags verified on 3.14 |
| Traefik    | v2.x       | IngressRoute CRDs bundled with k3s              |
| OpenSearch | 2.18.0     | image pulled in chart                           |

A **demo build** of every container is publicly hosted at:
```
public.ecr.aws/e8b9x6t1/<repo>:0.1.0
```
so the chart works out‑of‑the‑box (no private registry required).

---

## Repository layout

```
haystack-rag/
├── Chart.yaml
├── values.yaml              # all tunables
├── README.md                # ← this file
├── IMAGES.md                # how to rebuild & push images to ECR
├── .github/
│   └── workflows/
│       └── chart-ci.yml     # CI/CD testing workflow
├── tests/
│   ├── README.md            # comprehensive testing documentation
│   ├── run-tests.py         # main testing framework
│   ├── generate-report.py   # XUnit report generator
│   └── test-values.yaml     # test configuration values
└── templates/
    ├── _helpers.tpl         # name helpers & labels
    ├── namespace.yaml
    ├── secret.yaml          # OpenSearch + OpenAI keys
    ├── configmap.yaml       # runtime env vars
    ├── pvc-opensearch.yaml
    ├── statefulset-opensearch.yaml
    ├── deployment-indexing.yaml
    ├── deployment-query.yaml
    ├── deployment-frontend.yaml
    ├── service.yaml         # four Services (OpenSearch, indexing, query, UI)
    ├── middleware.yaml      # 100 MiB body limit
    ├── middleware-strip.yaml# strips /api for worker pods
    ├── transport.yaml       # extended proxy time‑outs
    └── ingressroute.yaml    # Traefik routing
```

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

## Building Images

See [`IMAGES.md`](./IMAGES.md) for instructions on how to build and push the required container images for Kubernetes deployments.

---

## Quick start

```bash
# clone the repo that contains the chart directory
cd haystack-rag

# create secrets override
auth_file=my-values.yaml
cat > $auth_file <<'EOF'
hostname: rag.local
secret:
  opensearchPassword: "Sup3rS3cret!"
  openaiApiKey:        "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
EOF

helm upgrade --install rag . \
  --namespace haystack-rag --create-namespace \
  -f $auth_file
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

After deploying the chart, use these steps to verify your deployment is healthy:

### 1. Check Pod and Service Status

```bash
kubectl get pods -n haystack-rag
kubectl get svc -n haystack-rag
kubectl get ingressroute -n haystack-rag
```

All pods should be in the `Running` or `Completed` state. Services and ingress routes should be listed.

### 2. Verify OpenSearch

Check OpenSearch readiness:

```bash
kubectl port-forward svc/opensearch 9200:9200 -n haystack-rag &
curl -u admin:<your-opensearchPassword> http://localhost:9200/
```

You should see OpenSearch version info in the response.

### 3. Access the UI

Open your browser to [http://rag.local:8080/](http://rag.local:8080/) (or your configured hostname/port). The Haystack RAG UI should load.

### 4. Check Logs

If something isn’t working, inspect logs:

```bash
kubectl logs deployment/rag-query -n haystack-rag
kubectl logs deployment/rag-indexing -n haystack-rag
kubectl logs deployment/rag-frontend -n haystack-rag
kubectl logs statefulset/opensearch -n haystack-rag
```

### 5. Troubleshooting

- Ensure all pods are running: `kubectl get pods -n haystack-rag`
- Check for CrashLoopBackOff or errors in logs
- Verify secrets and configmaps are mounted:  
  `kubectl describe pod <pod-name> -n haystack-rag`
- Confirm ingress or port-forwarding is set up correctly

---

## Values reference

The chart is fully parameterized and all major settings are grouped by component. Below is a summary of the most important values (see values.yaml for all options):

```yaml
namespace: haystack-rag
hostname: rag.local

secret:
  opensearchPassword: ChangeMe123!
  openaiApiKey: ""

frontend:
  replicaCount: 1
  port: 80
  service:
    type: ClusterIP
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi
  env:
    REACT_APP_HAYSTACK_API_URL: /api
    LOG_LEVEL: info
  livenessProbe:
    path: /
    initialDelaySeconds: 10
    periodSeconds: 10
  readinessProbe:
    path: /
    initialDelaySeconds: 5
    periodSeconds: 5

query:
  replicaCount: 1
  port: 8002
  service:
    type: ClusterIP
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  env:
    LOG_LEVEL: info
  livenessProbe:
    path: /health
    initialDelaySeconds: 10
    periodSeconds: 10
  readinessProbe:
    path: /health
    initialDelaySeconds: 5
    periodSeconds: 5

indexing:
  replicaCount: 1
  port: 8001
  service:
    type: ClusterIP
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  env:
    LOG_LEVEL: info
  livenessProbe:
    path: /health
    initialDelaySeconds: 10
    periodSeconds: 10
  readinessProbe:
    path: /health
    initialDelaySeconds: 5
    periodSeconds: 5

opensearch:
  replicaCount: 1
  port: 9200
  service:
    type: ClusterIP
  storageClass: local-path
  storageSize: 10Gi
  javaOpts: "-Xms512m -Xmx512m"
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1
      memory: 2Gi

ingress:
  enabled: true
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
    traefik.ingress.kubernetes.io/router.middlewares: haystack-rag-strip-api@kubernetescrd,haystack-rag-buffering@kubernetescrd
  buffering:
    enabled: true
    maxRequestBodyBytes: 104857600
    memRequestBodyBytes: 10485760
  timeouts:
    readTimeout: 600
    writeTimeout: 600
    idleTimeout: 600
```

**Key variables:**
- `replicaCount`: Number of pod replicas for each component
- `port`: Service and container port for each component
- `resources`: CPU/memory requests and limits
- `env`: Environment variables (e.g., log level, API URL)
- `livenessProbe`/`readinessProbe`: Health check paths and timings
- `service.type`: Kubernetes service type (ClusterIP, NodePort, etc.)
- `ingress.buffering`/`ingress.timeouts`: Traefik middleware settings

---

## Debugging & Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
|`NameResolutionError: 'opensearch'`| Service missing / mis‑named | `kubectl -n haystack-rag get svc opensearch` |
|Uploads >10 MiB return 413| buffering middleware not attached | check `ingressroute.yaml` annotation & route middlwares |
|`/files` 200 but `/search` 404| `/api` prefix not stripped | ensure `strip-api` middleware is on both API routes |
|Frontend loads but calls `http://localhost:8000/files`| **`REACT_APP_HAYSTACK_API_URL`** was baked incorrectly at **build time** | rebuild frontend image with `--build-arg REACT_APP_HAYSTACK_API_URL=/api` |

---

## GitHub Actions CI

A comprehensive workflow (**.github/workflows/chart-ci.yml**) is included:
1. **helm lint --strict** against `values.yaml`
2. **helm template** → **kubeconform -strict** to schema‑validate every object
3. **Python-based testing framework** for comprehensive chart validation
4. **Test report generation** in XUnit and JSON formats

Add it to your repo and each PR will be thoroughly tested before merging.

---

## Uninstall

```bash
helm uninstall rag -n haystack-rag
kubectl delete ns haystack-rag   # remove PVC & secrets
```

---

### Upstream project

This chart packages the demo code from **<https://github.com/deepset-ai/haystack-rag-app>**
into a single‑command deployment for local clusters.  Star the upstream repo for updates!

