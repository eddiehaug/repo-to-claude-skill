# Repo-to-Skill Converter 🤖

**AI-powered Streamlit app to automatically convert GitHub repositories into Claude Skills**

Transform any GitHub repository into a comprehensive Claude Skill with just one click! This tool uses Claude AI to analyze repositories and generate professional, well-structured skills following Anthropic's best practices.

---

## Features

✅ **AI-Powered Analysis**: Intelligently analyzes repository structure, documentation, and code using multiple AI providers

✅ **Flexible Authentication**: 4 authentication methods supported:
   - **Vertex AI** (Gemini 2.5 Flash/Pro, Claude Sonnet 4.5)
   - **Google AI Studio** (Gemini models with API key)
   - **Anthropic API** (Claude 3/3.5 models)
   - **OpenAI API** (GPT-4o, o1 models)

✅ **Secure by Design**: Production-ready security with input validation, HTTPS-only, and credential protection

✅ **Fully Automated**: Just provide a GitHub URL - the app handles everything else

✅ **Batch Processing**: Convert multiple repositories at once

✅ **Automatic Validation**: Validates skills using Anthropic's official validation script

✅ **Skill History**: Tracks all generated skills with ability to download or regenerate

✅ **One-Click Installation**: Automatically install to `~/.claude/skills/` or download as .zip

✅ **Modern UI**: Beautiful, responsive Streamlit interface with progress tracking

✅ **Progressive Disclosure**: Generated skills follow Anthropic's pattern with lean SKILL.md and detailed references

---

## Quick Start

### Prerequisites

- Python 3.10+
- Git installed on your system
- **Choose one authentication method**:
  - **Option 1 (Recommended): Vertex AI**
    - Google Cloud Project with Vertex AI API enabled
    - Authenticated with `gcloud auth application-default login`
    - No API key needed!
  - **Option 2: Google AI Studio**
    - Google API key ([Get one here](https://aistudio.google.com/apikey))
  - **Option 3: Anthropic API**
    - Anthropic API key ([Get one here](https://console.anthropic.com/))
  - **Option 4: OpenAI API**
    - OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone or navigate to this directory**:
```bash
cd repo-to-skill
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up authentication**:

**Option A: Vertex AI**

```bash
# Install Google Cloud SDK if not already installed
# See: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
```

Then create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and set your GCP project:
```
GCP_PROJECT_ID=your_project_id
GCP_LOCATION=us-central1
```

**Option B: Google AI Studio**

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
GOOGLE_API_KEY=your_api_key_here
```

**Option C: Anthropic API**

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

**Option D: OpenAI API**

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. **Run the app**:
```bash
streamlit run app.py
```

5. **Open your browser** to `http://localhost:8501`

---

## Usage

### Choosing Your AI Model

The app supports multiple AI models via 4 authentication methods:

**Via Vertex AI (Recommended)**:
- **Claude Sonnet 4.5** - Highest quality (default)
- **Gemini 2.5 Flash** - Fast, cost-effective alternative
- **Gemini 2.5 Pro** - More capable, better for complex repositories

**Via Google AI Studio**:
- **Gemini 2.5 Flash** - Fast and efficient (default)
- **Gemini 2.5 Pro** - Advanced model
- **Gemini 2.0 Flash (Experimental)** - Latest experimental features

**Via Anthropic API**:
- **Claude 3.5 Sonnet** - Latest Claude model (default)
- **Claude 3.5 Haiku** - Fast and efficient
- **Claude 3 Opus** - Most capable

**Via OpenAI API**:
- **GPT-4o Mini** - Efficient and fast (default)
- **GPT-4o** - Latest GPT-4 Optimized
- **GPT-4 Turbo** - High capability
- **o1-preview** - Advanced reasoning model

### Single Repository Conversion

1. Open the app in your browser
2. **Configure authentication** in the sidebar:
   - Select authentication method: "Vertex AI", "Google AI Studio", "Anthropic API", or "OpenAI API"
   - For Vertex AI: Enter your GCP Project ID and location
   - For API-based methods: Enter your API key
3. **Select your model** from the dropdown
4. Go to the **Generate** tab
5. Paste a GitHub repository URL (e.g., `https://github.com/owner/repo`)
6. Click **Generate Skill**
7. Wait for the AI to analyze and generate the skill
8. Choose to install directly or download the .zip file

### Batch Conversion

1. Go to the **Batch Generate** tab
2. Enter multiple GitHub URLs (one per line)
3. Click **Generate All Skills**
4. Each repository will be processed sequentially
5. Download or install each skill individually

### View History

- Click on **History** in the sidebar
- See all previously generated skills
- Re-download skills as needed
- View generation statistics

---

## How It Works

The app follows a comprehensive 5-step process:

### 1. **Cloning** 🔄
- Validates the GitHub URL
- Clones the repository to a temporary directory
- Fetches repository metadata from GitHub API

### 2. **Analyzing** 🔍
- Extracts README content
- Analyzes file structure
- Identifies programming languages
- Detects repository type (SDK, framework, library, etc.)
- Extracts code samples
- Checks for documentation

### 3. **Generating** 🤖
- Sends repository analysis to Claude API
- AI creates comprehensive skill content:
  - SKILL.md with workflows and quick starts
  - Reference documentation (500-700 lines)
  - Code templates with examples
- Follows Anthropic's progressive disclosure pattern
- Uses imperative voice and objective tone

### 4. **Validating** ✅
- Validates YAML frontmatter
- Checks skill structure
- Ensures required files exist
- Verifies formatting

### 5. **Packaging** 📦
- Creates proper skill folder structure
- Packages to .zip file
- Optionally installs to `~/.claude/skills/`
- Saves to database for history tracking

---

## Generated Skill Structure

Each generated skill follows this professional structure:

```
skill-name/
├── SKILL.md                      # Main skill file with workflows
├── references/
│   ├── implementation-guide.md   # Detailed implementation docs
│   ├── api-reference.md          # API or concept reference
│   └── advanced-patterns.md      # Advanced usage patterns
└── assets/templates/
    ├── basic-example.py          # Basic working example
    ├── advanced-example.py       # Advanced use case
    └── integration-example.py    # Integration pattern
```

### SKILL.md Contents

- **YAML Frontmatter**: Name and description
- **Overview**: When to use this skill
- **Quick Start**: Installation and basic example
- **Core Workflows**: 3-5 step-by-step workflows
- **Key Concepts**: Main concepts explained
- **Reference Documentation**: Links to detailed docs
- **Templates**: Links to code examples
- **Best Practices**: Dos and don'ts
- **Troubleshooting**: Common issues

---

## Configuration

### Authentication Setup

#### Option 1: Vertex AI (Recommended)

**Advantages**:
- No API key management needed
- Access to both Gemini and Claude models
- Lower costs with Gemini Flash
- Enterprise-grade security with ADC

**Setup**:

1. **Install Google Cloud SDK**:
```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

2. **Authenticate**:
```bash
# Login and create application default credentials
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

3. **Enable APIs**:
```bash
# Enable Vertex AI
gcloud services enable aiplatform.googleapis.com

# Enable Gen AI (for Gemini/Claude models)
gcloud services enable generativelanguage.googleapis.com
```

4. **Set environment variables**:

Create `.env` file:
```bash
GCP_PROJECT_ID=your_project_id
GCP_LOCATION=us-central1  # Or your preferred region
GITHUB_TOKEN=your_github_token  # Optional
```

**Supported Models**:
- `claude-sonnet-4-5@20250929` - Claude via Vertex AI (default)
- `gemini-2.5-flash` - Fast, cost-effective
- `gemini-2.5-pro` - High capability

#### Option 2: Google AI Studio

**Advantages**:
- Simple setup with API key
- Direct access to latest Gemini models
- No Google Cloud account needed
- Free tier available

**Setup**:

1. Get API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

2. Create `.env` file:
```bash
GOOGLE_API_KEY=your_api_key_here
GITHUB_TOKEN=your_github_token  # Optional
```

**Supported Models**:
- `gemini-2.5-flash` - Fast and efficient (default)
- `gemini-2.5-pro` - Advanced model
- `gemini-2.0-flash-exp` - Experimental features

#### Option 3: Anthropic API

**Advantages**:
- Simple setup
- Direct access to Claude models
- Latest Claude features

**Setup**:

1. Get API key from [console.anthropic.com](https://console.anthropic.com/)

2. Create `.env` file:
```bash
ANTHROPIC_API_KEY=your_api_key_here
GITHUB_TOKEN=your_github_token  # Optional
```

**Supported Models**:
- `claude-3-5-sonnet-20241022` - Latest Sonnet (default)
- `claude-3-5-haiku-20241022` - Fast and efficient
- `claude-3-opus-20240229` - Most capable

#### Option 4: OpenAI API

**Advantages**:
- Access to GPT-4o and o1 models
- Simple API key setup
- Advanced reasoning with o1

**Setup**:

1. Get API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

2. Create `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
GITHUB_TOKEN=your_github_token  # Optional
```

**Supported Models**:
- `gpt-4o-mini` - Efficient and fast (default)
- `gpt-4o` - Latest GPT-4 Optimized
- `gpt-4-turbo` - High capability
- `o1-preview` - Advanced reasoning

---

### Environment Variables Reference

Create a `.env` file with:

```bash
# === Vertex AI Configuration (Option 1) ===
GCP_PROJECT_ID=your_project_id
GCP_LOCATION=us-central1

# === Google AI Studio Configuration (Option 2) ===
GOOGLE_API_KEY=your_google_api_key

# === Anthropic API Configuration (Option 3) ===
ANTHROPIC_API_KEY=your_anthropic_api_key

# === OpenAI API Configuration (Option 4) ===
OPENAI_API_KEY=your_openai_api_key

# === Optional ===
# GitHub Personal Access Token (for higher rate limits)
GITHUB_TOKEN=your_github_token_here
```

### Settings in config.py

You can customize various settings in `config.py`:

- `DEFAULT_VERTEX_MODEL`: Default AI model (default: claude-sonnet-4-5@20250929)
- `MAX_TOKENS`: Max tokens for generation (default: 32000)
- `CLAUDE_SKILLS_DIR`: Installation directory (default: ~/.claude/skills)
- `MAX_BATCH_SIZE`: Maximum repositories in batch mode (default: 5)
- `OUTPUT_DIR`: Where generated skills are saved
- Authentication methods and available models

---

## Project Structure

```
repo-to-skill/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration and constants
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
├── src/
│   ├── __init__.py
│   ├── repo_analyzer.py     # Repository cloning and analysis
│   ├── ai_generator.py      # Claude API integration
│   ├── skill_builder.py     # Skill structure creation
│   ├── validator.py         # Skill validation
│   ├── packager.py          # Packaging and installation
│   └── database.py          # SQLite database operations
├── templates/
│   ├── skill_prompt.txt     # AI generation prompt
│   └── custom_styles.css    # UI styling
├── data/
│   ├── skills_history.db    # SQLite database (auto-created)
│   └── temp/                # Temporary repository clones
└── output/
    └── generated/           # Generated .zip files and skills
```

---

## Examples

### Example 1: Convert Python SDK

```
URL: https://github.com/anthropics/anthropic-sdk-python

Generated Skill:
- Name: anthropic-python-sdk
- 3 core workflows (Installation, Basic Usage, Advanced Patterns)
- 2 reference docs (API Reference, Authentication Guide)
- 3 templates (Basic client, Streaming, Function calling)
```

### Example 2: Convert Framework

```
URL: https://github.com/google/adk-python

Generated Skill:
- Name: adk-python-framework
- 4 core workflows (Build Agent, Multi-Agent, Custom Tools, Deploy)
- 3 reference docs (Core Concepts, Quick Start, Deployment)
- 3 templates (Basic agent, Multi-agent, Custom tools)
```

---

## Troubleshooting

### App won't start

**Issue**: `ModuleNotFoundError`

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

---

### API Key errors

**Issue**: "Invalid API key"

**Solutions**:
- Check your API key in `.env` file
- Verify key is active at https://console.anthropic.com/
- Enter key directly in the sidebar

---

### Repository cloning fails

**Issue**: "Failed to clone repository"

**Solutions**:
- Ensure Git is installed
- Check repository URL is correct
- Verify repository is public
- Check network connection

---

### Validation fails

**Issue**: "Validation errors"

**Solutions**:
- This is usually not critical - skill may still work
- Check generated SKILL.md for proper YAML frontmatter
- Ensure references/ and templates/ have content

---

## Advanced Usage

### Custom Validation Script

By default, the app uses Anthropic's validation script from the parent directory. To use a custom validator:

1. Update `VALIDATION_SCRIPT` path in `config.py`
2. Ensure script accepts skill directory as argument

### Custom Skill Prompt

Modify `templates/skill_prompt.txt` to change how AI generates skills:

- Adjust structure requirements
- Change reference documentation format
- Modify code template requirements

### Database Management

The SQLite database stores all generation history. Access it directly:

```python
from src.database import SkillDatabase

db = SkillDatabase()
skills = db.get_all_skills()
stats = db.get_stats()
```

---

## Best Practices

### For Best Results

✅ **Use well-documented repositories**: The better the README, the better the generated skill

✅ **Convert established projects**: Mature repositories with examples generate better skills

✅ **Review AI output**: Always review generated content before using

✅ **Provide GitHub token**: Avoid rate limits with a personal access token

✅ **Start with single generation**: Test with one repo before batch processing

### What Works Best

- **SDKs and libraries**: Excellent results with clear APIs
- **Frameworks**: Good results with comprehensive docs
- **Example repositories**: Great for sample catalogs
- **Well-documented projects**: Better than sparsely documented ones

---

## Limitations

- **Public repositories only**: Cannot access private repos
- **Repository size**: Very large repos (>1000 files) may take longer
- **API costs**: Each skill generation uses Claude API tokens
- **Language support**: Best results with Python, JavaScript, TypeScript, Go
- **Documentation dependency**: Quality depends on repository documentation

---

## FAQ

**Q: Which authentication method should I use?**

A: **Recommended order**:
1. **Vertex AI** - Best if you have GCP access (no API key management, access to multiple models)
2. **Google AI Studio** - Simple API key setup, free tier available for Gemini models
3. **Anthropic API** - Direct access to latest Claude models
4. **OpenAI API** - If you need GPT-4o or advanced reasoning with o1

**Q: Which model should I choose?**

A: **For best quality**: Claude Sonnet 4.5 (Vertex AI) or Claude 3.5 Sonnet (Anthropic API)

**For cost-effectiveness**: Gemini 2.5 Flash (Vertex AI or Google AI Studio) or GPT-4o Mini (OpenAI)

**For complex repositories**: Gemini 2.5 Pro, Claude 3 Opus, or GPT-4o

**Q: How much does it cost to generate a skill?**

A: **Vertex AI**:
- Gemini 2.5 Flash: ~$0.01-0.05 per skill
- Gemini 2.5 Pro: ~$0.05-0.20 per skill
- Claude Sonnet 4.5: ~$0.10-0.50 per skill

**Google AI Studio**:
- Gemini models: Free tier available, then similar to Vertex AI pricing

**Anthropic API**:
- Claude 3.5 Sonnet: ~$0.10-0.50 per skill
- Claude 3.5 Haiku: ~$0.05-0.15 per skill
- Claude 3 Opus: ~$0.50-1.50 per skill

**OpenAI API**:
- GPT-4o Mini: ~$0.02-0.10 per skill
- GPT-4o: ~$0.20-0.80 per skill
- o1-preview: ~$0.50-2.00 per skill

(Costs vary based on repository size and documentation)

**Q: Can I customize the generated skills?**

A: Yes! Generated skills are in output/generated/ - edit before packaging or installing.

**Q: Will this work with private repositories?**

A: Not currently. Only public GitHub repositories are supported.

**Q: Can I regenerate a skill?**

A: Yes, just enter the same URL again. The app will create a new version.

**Q: Where are skills installed?**

A: `~/.claude/skills/` directory (configurable in config.py)

---

## Security

This application implements production-ready security controls:

✅ **Input Validation**: All GitHub URLs validated with regex, length limits, and HTTPS-only enforcement

✅ **Path Traversal Prevention**: Sanitized paths with containment verification

✅ **Resource Limits**: 500MB repository limit, 1MB README limit, file size restrictions

✅ **Command Injection Prevention**: Safe GitPython API usage, no shell execution

✅ **SQL Injection Prevention**: Parameterized queries throughout

✅ **Credential Protection**: Masked API key inputs, no logging of sensitive data, environment variable support

✅ **Secure Defaults**: HTTPS-only, strict validation, automatic cleanup

For detailed security information, see [SECURITY.md](SECURITY.md).

---

## Contributing

Contributions welcome! Areas for improvement:

- Support for private repositories
- GitLab/Bitbucket support
- More customizable templates
- Skill editing before generation
- Better error handling
- Performance optimizations

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Anthropic** for Claude AI and Skills framework
- **Streamlit** for the amazing web framework
- **GitHub** for repository hosting and API

---

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review generated logs in the app
3. Check Streamlit console output for errors

---

**Built with ❤️ using Claude AI and Streamlit**

Version 1.0.0
