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

See [`tests/README.md`](./tests/README.md) for comprehensive documentation on the Python-based testing framework, how to run tests locally, and CI integration details.

---

## Building Images

See [`IMAGES.md`](./IMAGES.md) for instructions on how to build and push the required container images for Kubernetes deployments.

---

## Quick start

```bash
# clone the repo that contains the chart directory
# git clone https://github.com/your‑fork/haystack‑rag‑app.git
cd haystack‑rag‑app/charts/haystack-rag

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

## Values reference (excerpt)

<<<<<<< Updated upstream
| Key | Default | Description |
|-----|---------|-------------|
| `hostname`              | `rag.local` | Ingress host header |
| `image.registry`        | `public.ecr.aws/e8b9x6t1` | change if you push to private ECR |
| `image.tag`             | `0.1.0`     | set to your build tag |
| `secret.*`              | *empty*     | OpenSearch admin pwd & OpenAI key |
| `opensearch.storageSize`| `10Gi`      | PVC size |
| `resources.*`           | `{}`        | add CPU/RAM requests/limits |
=======
The chart is fully parameterized and all major settings are grouped by component. See [`values.yaml`](./values.yaml) for all available options and defaults.

**Key variables:**
- `replicaCount`: Number of pod replicas for each component
- `port`: Service and container port for each component
- `resources`: CPU/memory requests and limits
- `env`: Environment variables (e.g., log level, API URL)
- `livenessProbe`/`readinessProbe`: Health check paths and timings
- `service.type`: Kubernetes service type (ClusterIP, NodePort, etc.)
- `ingress.buffering`/`ingress.timeouts`: Traefik middleware settings
>>>>>>> Stashed changes

---

## Debugging & Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
|`NameResolutionError: 'opensearch'`| Service missing / mis‑named | `kubectl -n haystack-rag get svc opensearch` |
|Uploads >10 MiB return 413| buffering middleware not attached | check `ingressroute.yaml` annotation & route middlwares |
|`/files` 200 but `/search` 404| `/api` prefix not stripped | ensure `strip-api` middleware is on both API routes |
|Frontend loads but calls `http://localhost:8000/files`| **`REACT_APP_HAYSTACK_API_URL`** was baked incorrectly at **build time** → rebuild frontend image with `--build-arg REACT_APP_HAYSTACK_API_URL=/api` |

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

