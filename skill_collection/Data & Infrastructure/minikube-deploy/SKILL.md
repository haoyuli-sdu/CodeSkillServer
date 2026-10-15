---
name: "minikube-deploy"
description: "Zero-shot deployment of ANY containerized application to local Kubernetes using Minikube. Use when Claude needs to: (1) Deploy any project to Minikube without prior setup, (2) Auto-detect services from Dockerfiles or docker-compose.yml, (3) Generate Helm charts dynamically for detected services, (4) Build and deploy multiple services automatically, (5) Enable optional Dapr for event-driven architecture, (6) Migrate any docker-compose project to Kubernetes. Works with monorepos, single apps, any number of services. Cross-platform (Linux, macOS, Windows). Triggers: 'deploy to minikube', 'run on kubernetes locally', 'local k8s', 'minikube deployment'."
---

# Minikube Deploy (Zero-Shot)

Deploy ANY project to Minikube in a single iteration with automatic service detection and Helm chart generation.

## Zero-Shot Workflow

```
PREREQ → DETECT (services + Dapr) → GENERATE → BUILD → DEPLOY → VERIFY
```

Execute ALL steps without stopping. Only ask user if:
- Critical info is missing
- Dapr detection score is 2-4 (ambiguous - ask "Enable Dapr?")

---

## Step 0: PREREQUISITES

Run prerequisite check first to catch issues early:

```bash
# Check all requirements
.claude/skills/minikube-deploy/assets/scripts/check-prerequisites.sh
```

Or manually verify:
- Docker installed and running
- Minikube installed
- kubectl installed
- Helm installed
- At least one Dockerfile exists

**Cross-Platform Docker Setup:**

```bash
# Linux/macOS/Git Bash
eval $(minikube docker-env)

# Windows PowerShell
& minikube docker-env --shell powershell | Invoke-Expression

# Windows CMD
@FOR /f "tokens=*" %i IN ('minikube docker-env --shell cmd') DO @%i
```

---

## Step 1: DETECT

### 1.1 Find Services

```bash
# Find all Dockerfiles
find . -name "Dockerfile" -o -name "Dockerfile.*" 2>/dev/null | grep -v node_modules | grep -v .git

# Check for docker-compose
ls docker-compose*.yml docker-compose*.yaml compose*.yml 2>/dev/null

# Find env files
find . -name ".env" -o -name ".env.example" 2>/dev/null | grep -v node_modules | head -5
```

### 1.2 Parse Each Dockerfile

For each Dockerfile, extract:

```bash
# Port
grep -i "^EXPOSE" <path> | awk '{print $2}' | head -1

# Service name = parent folder name
dirname <path> | xargs basename
```

### 1.3 Detect Health Probe Paths

Use the health probe detector or scan code:

```bash
# Auto-detect health endpoints
.claude/skills/minikube-deploy/assets/scripts/detect-health-probes.sh
```

**Framework defaults if not detected:**

| Framework | Default Health Path |
|-----------|-------------------|
| FastAPI | `/health` |
| Next.js | `/api/health` |
| Express | `/health` |
| Spring | `/actuator/health` |
| Django | `/health/` |
| Unknown | `/` |

### 1.4 Build Service Map

```
PROJECT_NAME = <root-folder-name>
SERVICES = [
  {name: "api", path: "apps/api", port: 8000, type: "backend", healthPath: "/health"},
  {name: "frontend", path: "apps/frontend", port: 3000, type: "frontend", healthPath: "/"},
  ...
]
```

**Type detection:**
- Port 3000/3001/5173 + (next|react|vue|vite) → frontend
- Port 8000/8080/5000 + (fastapi|flask|express) → backend/api
- No EXPOSE or worker/job in name → worker

### 1.5 Detect Dapr Requirement

Run the Dapr detector to determine if Dapr should be enabled:

```bash
.claude/skills/minikube-deploy/assets/scripts/detect-dapr-need.sh
```

**Auto-detection triggers (score-based):**

| Indicator | Score | Meaning |
|-----------|-------|---------|
| Existing Dapr config | +10 | Dapr required |
| Kafka/Redpanda in compose | +3 | Event streaming |
| Redis in compose | +2 | Pub/sub or state |
| DaprClient in code | +5 | Already using Dapr |
| Pub/sub patterns | +2 | Event-driven code |
| 3+ services | +2 | Microservices |

**Decision logic:**
- Score >= 5 → **Enable Dapr automatically**
- Score 2-4 → **Ask user**: "Enable Dapr for event-driven features?"
- Score < 2 → **Skip Dapr** (simple deployment)

Set `DAPR_ENABLED=true/false` for subsequent steps.

---

## Step 2: GENERATE

### 2.1 Create Helm Structure

```bash
PROJECT="<detected-name>"
mkdir -p helm/$PROJECT/templates
```

### 2.2 Chart.yaml

```yaml
# helm/$PROJECT/Chart.yaml
apiVersion: v2
name: $PROJECT
description: Auto-generated chart for $PROJECT
type: application
version: 1.0.0
appVersion: "1.0.0"
```

### 2.3 values.yaml

Generate dynamically based on detected services:

```yaml
# helm/$PROJECT/values.yaml
namespace: $PROJECT
imagePullPolicy: IfNotPresent

configMap:
  NODE_ENV: "production"

# Dapr configuration (if DAPR_ENABLED=true)
dapr:
  enabled: $DAPR_ENABLED  # true or false based on Step 1.5
  logLevel: "info"
  pubsub:
    type: "pubsub.redis"  # or pubsub.kafka
  statestore:
    type: "state.redis"

# Repeat for EACH detected service:
$SERVICE_NAME:
  enabled: true
  replicaCount: 1
  image:
    repository: $SERVICE_NAME
    tag: latest
  service:
    type: ClusterIP  # NodePort for external
    port: $DETECTED_PORT
  resources:
    requests: {cpu: 100m, memory: 128Mi}
    limits: {cpu: 200m, memory: 256Mi}
  probes:
    enabled: true
    path: /health  # or / for frontends
```

### 2.4 Templates

**_helpers.tpl:**
```yaml
{{- define "$PROJECT.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
```

**configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "$PROJECT.fullname" . }}-config
  namespace: {{ .Values.namespace }}
data:
  {{- range $key, $value := .Values.configMap }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
```

**For EACH service, create templates/$SERVICE/deployment.yaml:**
```yaml
{{- if .Values.$SERVICE.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "$PROJECT.fullname" . }}-$SERVICE
  namespace: {{ .Values.namespace }}
  labels:
    app.kubernetes.io/name: $SERVICE
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  replicas: {{ .Values.$SERVICE.replicaCount }}
  selector:
    matchLabels:
      app: $SERVICE
  template:
    metadata:
      labels:
        app: $SERVICE
        app.kubernetes.io/name: $SERVICE
      {{- if .Values.dapr.enabled }}
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{{ include "$PROJECT.fullname" . }}-$SERVICE"
        dapr.io/app-port: "{{ .Values.$SERVICE.service.port }}"
        dapr.io/log-level: "{{ .Values.dapr.logLevel }}"
      {{- end }}
    spec:
      containers:
        - name: $SERVICE
          image: "{{ .Values.$SERVICE.image.repository }}:{{ .Values.$SERVICE.image.tag }}"
          imagePullPolicy: {{ .Values.imagePullPolicy }}
          ports:
            - containerPort: {{ .Values.$SERVICE.service.port }}
          envFrom:
            - configMapRef:
                name: {{ include "$PROJECT.fullname" . }}-config
          resources:
            {{- toYaml .Values.$SERVICE.resources | nindent 12 }}
{{- end }}
```

**For EACH service, create templates/$SERVICE/service.yaml:**
```yaml
{{- if .Values.$SERVICE.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: $SERVICE
  namespace: {{ .Values.namespace }}
spec:
  type: {{ .Values.$SERVICE.service.type }}
  ports:
    - port: {{ .Values.$SERVICE.service.port }}
      targetPort: {{ .Values.$SERVICE.service.port }}
  selector:
    app: $SERVICE
{{- end }}
```

---

## Step 3: BUILD

### 3.1 Setup Minikube Docker

```bash
# Start minikube if needed
minikube status || minikube start --driver=docker --cpus=2 --memory=4096

# Use minikube's Docker daemon
eval $(minikube docker-env)
```

### 3.2 Build Each Image

For EACH detected service:

```bash
docker build -t $SERVICE_NAME:latest -f $DOCKERFILE_PATH $CONTEXT_PATH
```

**Context rules:**
- `apps/api/Dockerfile` → context = `apps/api`
- `./Dockerfile` → context = `.`
- `services/worker/Dockerfile` → context = `services/worker`

### 3.3 Verify

```bash
docker images | grep -E "service1|service2|..."
```

---

## Step 4: DEPLOY

### 4.1 Create Namespace

```bash
kubectl create namespace $PROJECT --dry-run=client -o yaml | kubectl apply -f -
```

### 4.2 Install Dapr (if DAPR_ENABLED=true)

**Only if Dapr was detected/requested in Step 1.5:**

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr control plane
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Verify Dapr is running
kubectl get pods -n dapr-system
# Expected: dapr-operator, dapr-sentry, dapr-sidecar-injector, dapr-placement
```

**Install Redis for Dapr (if using Redis backend):**

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm upgrade --install redis bitnami/redis \
  --namespace $PROJECT \
  --set auth.enabled=false \
  --set architecture=standalone \
  --wait
```

### 4.3 Create Secrets (if .env exists)

```bash
kubectl create secret generic $PROJECT-secrets \
  --namespace=$PROJECT \
  --from-env-file=.env \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 4.4 Deploy Dapr Components (if DAPR_ENABLED=true)

Create Dapr components for pub/sub and state store. See [references/dapr-integration.md](references/dapr-integration.md) for templates.

### 4.5 Helm Deploy

```bash
helm upgrade --install $PROJECT ./helm/$PROJECT \
  --namespace $PROJECT \
  --wait --timeout 5m
```

---

## Step 5: VERIFY

```bash
# Pods
kubectl get pods -n $PROJECT

# Services
kubectl get svc -n $PROJECT

# Quick log check
kubectl logs -l app.kubernetes.io/instance=$PROJECT -n $PROJECT --tail=10
```

### Access Instructions

Provide port-forward commands:
```bash
# For each service that needs external access:
kubectl port-forward svc/$SERVICE $LOCAL_PORT:$SERVICE_PORT -n $PROJECT
```

---

## Dapr Integration Summary

Dapr is automatically detected in Step 1.5 and enabled if:
- Existing Dapr configuration found
- Kafka/Redpanda/Redis detected in docker-compose
- DaprClient or pub/sub patterns in code
- User explicitly requests it

When Dapr is enabled:
1. Dapr control plane installed in `dapr-system` namespace
2. Redis installed for pub/sub and state store
3. Dapr annotations added to deployments
4. Dapr components created for pub/sub and state

**For detailed Dapr setup:** See [references/dapr-integration.md](references/dapr-integration.md)

---

## Common Patterns

| Project Type | Detection | Services |
|-------------|-----------|----------|
| Monorepo `apps/*` | Multiple Dockerfiles in apps/ | One per app |
| Single app | One Dockerfile in root | Single service |
| docker-compose | Parse compose file | Match compose services |
| Microservices | services/ or packages/ | One per directory |

## Port Defaults

| Type | Port | NodePort |
|------|------|----------|
| Frontend | 3000 | 30000 |
| API | 8000 | 30010 |
| Worker | N/A | N/A |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| ImagePullBackOff | `eval $(minikube docker-env)` before build |
| CrashLoopBackOff | `kubectl logs <pod> -n <ns>` |
| Connection refused | `kubectl port-forward svc/<name> <port>` |
| IPv6/ETIMEDOUT | See [common-issues.md](references/common-issues.md#external-database-connectivity) |
| Windows issues | See [common-issues.md](references/common-issues.md#windows-specific-issues) |

**For detailed troubleshooting:** See [references/common-issues.md](references/common-issues.md)

---

## Error Recovery

If deployment fails:

1. **Check logs:** `kubectl logs <pod> -n <namespace> --previous`
2. **Check events:** `kubectl get events -n <namespace> --sort-by='.lastTimestamp'`
3. **Cleanup and retry:**
   ```bash
   helm uninstall <project> -n <namespace>
   kubectl delete namespace <namespace>
   # Fix issue, then re-run deployment
   ```

---

## References

- [references/common-issues.md](references/common-issues.md) - **Troubleshooting guide**
- [references/dapr-integration.md](references/dapr-integration.md) - Dapr setup
- [references/health-checks.md](references/health-checks.md) - Probes
- [references/helm-structure.md](references/helm-structure.md) - Helm patterns

## Scripts

- `assets/scripts/check-prerequisites.sh` - Validate environment
- `assets/scripts/setup-docker-env.sh` - Cross-platform Docker setup
- `assets/scripts/detect-health-probes.sh` - Auto-detect health endpoints
- `assets/scripts/detect-dapr-need.sh` - Determine if Dapr is needed
