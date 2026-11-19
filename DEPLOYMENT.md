# Deployment Guide

## Quick start — local (no Docker)

```bash
# 1. Clone and enter the project
git clone https://github.com/Nawfal-AI/insurance_agent_production
cd insurance_agent_production

# 2. Create a virtual environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your LLM provider
cp .env.example .env
# Edit .env — set LLM_PROVIDER and the matching API key

# 5. Start the API server
uvicorn serve:app --reload --port 8080
# API: http://localhost:8080
# UI:  http://localhost:8080  (built-in HTML frontend)
# Health: http://localhost:8080/health

# 6. (Optional) Start the Streamlit frontend in a second terminal
pip install streamlit
streamlit run app/frontend/streamlit_app.py
# Frontend: http://localhost:8501
```

---

## Local with Docker Compose (mirrors production)

```bash
# Build and start both API + Streamlit frontend
docker-compose up --build

# API:      http://localhost:8080
# Frontend: http://localhost:8501

# Stop
docker-compose down
```

---

## AWS deployment (ECS Fargate)

### Prerequisites
- AWS CLI installed and configured (`aws configure`)
- Docker installed
- An ECR repository created for the image

### Step 1 — Push the image to ECR

```bash
# Set your values
AWS_REGION=eu-central-1
AWS_ACCOUNT=123456789012
ECR_REPO=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/insurance-agent

# Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REPO

# Build and push
docker build -t $ECR_REPO:latest .
docker push $ECR_REPO:latest
```

### Step 2 — Store secrets in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name insurance-agent/anthropic-api-key \
  --secret-string "your-anthropic-api-key" \
  --region $AWS_REGION
```

### Step 3 — Register the ECS task definition

```bash
# Edit infra/aws/ecs_task_definition.json — replace YOUR_ACCOUNT_ID and YOUR_ECR_URI
aws ecs register-task-definition \
  --cli-input-json file://infra/aws/ecs_task_definition.json \
  --region $AWS_REGION
```

### Step 4 — Create / update the ECS service

```bash
# If service already exists:
aws ecs update-service \
  --cluster your-cluster-name \
  --service your-service-name \
  --force-new-deployment \
  --region $AWS_REGION

# Verify deployment
aws ecs describe-services \
  --cluster your-cluster-name \
  --services your-service-name \
  --region $AWS_REGION \
  --query 'services[0].deployments'
```

### Step 5 — Set up CloudWatch logging

```bash
# Create the log group (ECS will create log streams automatically)
aws logs create-log-group \
  --log-group-name /ecs/insurance-agent \
  --region $AWS_REGION

# Optional: set a 30-day retention policy
aws logs put-retention-policy \
  --log-group-name /ecs/insurance-agent \
  --retention-in-days 30 \
  --region $AWS_REGION
```

---

## CI/CD (automated via GitHub Actions)

After the initial manual deploy above, every push to `main` will:
1. Run lint + tests
2. Build and push a new Docker image to ECR (tagged with the commit SHA)
3. Trigger an ECS rolling deployment

**Setup:** Add these secrets in your GitHub repo under Settings → Secrets → Actions:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REPOSITORY`
- `ECS_CLUSTER`
- `ECS_SERVICE`
- `GROQ_API_KEY` (used by tests in CI)

---

## MLflow experiment tracking (local)

```bash
pip install mlflow pyyaml

# Run an experiment (logs config + metrics)
python mlops/mlflow/track_experiment.py

# Open MLflow UI
mlflow ui
# Open http://localhost:5000
```

---

## Running tests

```bash
pytest tests/ -v
```
