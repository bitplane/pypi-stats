# Deployment Setup

This document explains how to set up the automated PyPI stats system in GitHub Actions.

## Required GitHub Secrets

Set these in your GitHub repository settings under Settings → Secrets and variables → Actions:

### 1. `GCP_SA_KEY`
Service account key for Google Cloud BigQuery access.

```bash
# Create a service account in Google Cloud Console
gcloud iam service-accounts create pypi-stats-bot \
  --description="Service account for PyPI stats automation" \
  --display-name="PyPI Stats Bot"

# Get your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Grant BigQuery access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:pypi-stats-bot@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:pypi-stats-bot@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

# Create and download the key
gcloud iam service-accounts keys create key.json \
  --iam-account=pypi-stats-bot@$PROJECT_ID.iam.gserviceaccount.com

# Copy the entire contents of key.json into the GCP_SA_KEY secret
```

### 2. `GCP_PROJECT`
Your Google Cloud Project ID (e.g., `pypi-stats-30335`)

### 3. `DEPLOY_SSH_KEY`
Private SSH key for pushing to your website repository.

```bash
# Generate a new SSH key (don't use your personal one)
ssh-keygen -t ed25519 -f deploy_key -N ""

# Add the public key (deploy_key.pub) to your website repository's deploy keys
# Copy the private key (deploy_key) content into the DEPLOY_SSH_KEY secret
```

## Manual Testing

Test the workflow manually:

```bash
# Test locally first
make USERNAME=davidsong

# Test the full deployment
make deploy

# Trigger the GitHub Action manually from the Actions tab
```

## Automation Schedule

The workflow runs automatically on the 1st of each month at 02:00 UTC.

It will:
1. Generate new stats for the current month
2. Update the cache with any new data
3. Commit and push cache changes
4. Deploy the updated PNG to your website

## Makefile Targets

- `make venv` - Create virtual environment
- `make stats.ansi` - Generate ANSI chart output
- `make stats.png` - Convert ANSI to PNG
- `make deploy` - Deploy PNG to website
- `make clean` - Clean up generated files and venv