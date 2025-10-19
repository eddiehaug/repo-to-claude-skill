# Vertex AI Setup Guide

Quick guide to set up Vertex AI authentication for the Repo-to-Skill Converter.

## Why Vertex AI?

✅ **No API Key Management** - Uses Application Default Credentials
✅ **Multiple Models** - Access Gemini 2.5 Flash, Pro, and Claude Sonnet 4.5
✅ **Cost Effective** - Gemini Flash is ~10x cheaper than Claude API
✅ **Enterprise Security** - Integrates with Google Cloud IAM

---

## One-Time Setup

### 1. Install Google Cloud SDK

**macOS**:
```bash
brew install google-cloud-sdk
```

**Linux**:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows**:
Download from: https://cloud.google.com/sdk/docs/install

### 2. Authenticate

```bash
# Login and create application default credentials
gcloud auth application-default login
```

This will open your browser for authentication. Once complete, your credentials are saved locally at:
- macOS/Linux: `~/.config/gcloud/application_default_credentials.json`
- Windows: `%APPDATA%\gcloud\application_default_credentials.json`

### 3. Set Your Project

```bash
# Replace with your actual project ID
gcloud config set project YOUR_PROJECT_ID

# Verify
gcloud config get-value project
```

### 4. Enable Required APIs

```bash
# Enable Vertex AI
gcloud services enable aiplatform.googleapis.com

# Enable Generative AI API
gcloud services enable generativelanguage.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled | grep -E "aiplatform|generativelanguage"
```

### 5. Configure Environment Variables

Create `.env` file in the repo-to-skill directory:

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
GCP_PROJECT_ID=your-actual-project-id
GCP_LOCATION=us-central1
```

**Available Locations**:
- `us-central1` (recommended)
- `us-east1`
- `europe-west1`
- `asia-northeast1`

---

## Testing Your Setup

### Verify Authentication

```bash
# Check if authenticated
gcloud auth application-default print-access-token

# If this prints a token, you're authenticated!
```

### Test in Python

Create `test_vertex.py`:

```python
from google import genai

client = genai.Client(
    vertexai=True,
    project="YOUR_PROJECT_ID",
    location="us-central1"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello!"
)

print(response.text)
```

Run:
```bash
python test_vertex.py
```

If you see a response, Vertex AI is working!

---

## Model Selection

### Gemini 2.5 Flash
- **Best for**: Most repositories, fast generation
- **Cost**: ~$0.01-0.05 per skill
- **Speed**: ~30-60 seconds per skill
- **Quality**: Very good

### Gemini 2.5 Pro
- **Best for**: Complex repositories, extensive docs
- **Cost**: ~$0.05-0.20 per skill
- **Speed**: ~60-120 seconds per skill
- **Quality**: Excellent

### Claude Sonnet 4.5 (via Vertex AI)
- **Best for**: Highest quality output
- **Cost**: ~$0.10-0.50 per skill
- **Speed**: ~60-90 seconds per skill
- **Quality**: Premium
- **Note**: May require specific regions

---

## Troubleshooting

### Error: "Could not automatically determine credentials"

**Solution**:
```bash
gcloud auth application-default login
```

### Error: "Project does not exist"

**Solution**:
```bash
# List your projects
gcloud projects list

# Set the correct project
gcloud config set project YOUR_PROJECT_ID
```

### Error: "API not enabled"

**Solution**:
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

### Error: "Permission denied"

**Solution**:
Ensure your account has the following roles:
- `roles/aiplatform.user`
- `roles/ml.developer`

Grant via Console or:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:YOUR_EMAIL" \
    --role="roles/aiplatform.user"
```

### Error: "Model not found"

**Solution**:
- Ensure you're in a supported region
- Claude Sonnet 4.5 may not be available in all regions
- Try `us-central1` or `us-east1`

---

## Cost Management

### Set Budget Alerts

1. Go to: https://console.cloud.google.com/billing/budgets
2. Create budget for your project
3. Set alerts at 50%, 80%, 100%

### Monitor Usage

```bash
# View recent Vertex AI usage
gcloud ai operations list --filter="metadata.@type:type.googleapis.com/google.cloud.aiplatform.v1.GenAiTuningServiceMetadata"
```

Or check in Console:
https://console.cloud.google.com/vertex-ai/

---

## Switching Between Accounts

If you have multiple Google Cloud accounts:

```bash
# List accounts
gcloud auth list

# Switch account
gcloud config set account ACCOUNT_EMAIL

# Re-authenticate for ADC
gcloud auth application-default login --account ACCOUNT_EMAIL
```

---

## Using Service Accounts (Optional)

For production deployments, use a service account:

1. **Create service account**:
```bash
gcloud iam service-accounts create skill-generator \
    --display-name="Skill Generator"
```

2. **Grant permissions**:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:skill-generator@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

3. **Create key**:
```bash
gcloud iam service-accounts keys create ~/skill-generator-key.json \
    --iam-account=skill-generator@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

4. **Set environment variable**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/skill-generator-key.json
```

---

## Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Google Gen AI SDK](https://github.com/googleapis/python-genai)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)

---

## Quick Reference

```bash
# Setup (one-time)
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com

# Verify
gcloud auth application-default print-access-token
gcloud config get-value project

# Run app
cd repo-to-skill
streamlit run app.py
```

---

**Need Help?**

Check the main [README.md](README.md) or create an issue on GitHub.
