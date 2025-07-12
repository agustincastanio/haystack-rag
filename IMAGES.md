# Building & pushing images to AWS ECR Public

This repo ships a **public demo build** of every container at `public.ecr.aws/e8b9x6t1/*`. You can deploy the chart out‑of‑the‑box without building anything.

If you need custom code or newer tags, follow the steps below.

---

## 1  Prerequisites

| Tool    | Tested version                                                    |
| ------- | ----------------------------------------------------------------- |
| Docker  | 24.x                                                              |
| AWS CLI |  v2.15+ (logged‑in user/role must have `ecr-public:*` push perms) |
| jq      |  any (only for optional digest checks)                            |

The public ECR registry lives **only in **``.

```bash
REG_ALIAS=e8b9x6t1            # your public registry alias
REG_ROOT="public.ecr.aws/$REG_ALIAS"
REGION=us-east-1
```

---

## 2  Authenticate Docker → ECR Public

```bash
aws ecr-public get-login-password --region $REGION \
  | docker login --username AWS --password-stdin public.ecr.aws
```

Token is valid for \~12 hours.

---

## 3  Build & push all three components

```bash
TAG=0.1.0   # or "+$(git rev-parse --short HEAD)"

docker build -t $REG_ROOT/haystack-indexing:$TAG \
             -f backend/Dockerfile.indexing backend

docker build -t $REG_ROOT/haystack-query:$TAG \
             -f backend/Dockerfile.query backend

docker build -t $REG_ROOT/haystack-frontend:$TAG \
             -f frontend/Dockerfile.frontend frontend

# push
for img in indexing query frontend; do
  docker push $REG_ROOT/haystack-$img:$TAG
done
```

### Multi‑arch (AMD64 + ARM64) in one go

```bash
docker buildx build --push --platform linux/amd64,linux/arm64 \
     -t $REG_ROOT/haystack-indexing:$TAG -f backend/Dockerfile.indexing backend
# …repeat for query & frontend
```

---

## 4  Point the chart at your tag

```bash
helm upgrade rag ./haystack-rag \
  -n haystack-rag \
  --reuse-values \
  --set image.tag="$TAG"
```

You can also override `image.registry` if you push to a private ECR.

---

## 5  Digest sanity check (optional)

```bash
REMOTE=$(aws ecr-public describe-images \
          --region $REGION \
          --registry-id $(aws sts get-caller-identity --query Account --output text) \
          --repository-name haystack-indexing \
          --image-ids imageTag=$TAG \
          --query 'imageDetails[0].imageDigest' --output text)

echo "Remote digest: $REMOTE"
```

Match this digest with what `kubectl get pods -o jsonpath='{..imageID}'` shows inside the cluster to confirm the pull succeeded.

