# Deployment Setup

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

### 3. `DEPLOY_PAT`
Fine-grained Personal Access Token for pushing to your website repository.

1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Click "Generate new token"
3. Give it a name like "pypi-stats-deploy"
4. Set expiration to never 
5. Under "Repository access", select "Selected repositories" and choose only `bitplane/bitplane.net`
6. Under "Repository permissions", grant ONLY:
   - **Contents**: Read and Write (to push the PNG file)
   - **Metadata**: Read (automatically required)
7. Generate the token and copy it
8. Add it as `DEPLOY_PAT` secret in your pypi-stats repository settings


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
4. Deploy the updated SVG to your website

## Makefile Targets

- `make venv` - Create virtual environment
- `make stats.ansi` - Generate ANSI chart output
- `make stats.svg` - Convert ANSI to SVG
- `make deploy` - Deploy SVG to website
- `make clean` - Clean up generated files and venv
