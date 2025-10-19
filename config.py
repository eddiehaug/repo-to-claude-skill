"""
Configuration for Repo-to-Skill Converter
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = DATA_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output" / "generated"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "skills_history.db"

# AI Model Configuration
# Authentication methods
AUTH_METHODS = ["Vertex AI", "Google AI Studio", "Anthropic API", "OpenAI API"]

# Available models by authentication method
VERTEX_AI_MODELS = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Claude Sonnet 4.5": "claude-sonnet-4-5@20250929"
}

GOOGLE_AI_STUDIO_MODELS = {
    "Gemini 2.0 Flash (Experimental)": "gemini-2.0-flash-exp",
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro"
}

ANTHROPIC_API_MODELS = {
    "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022",
    "Claude 3.5 Haiku": "claude-3-5-haiku-20241022",
    "Claude 3 Opus": "claude-3-opus-20240229"
}

OPENAI_API_MODELS = {
    "GPT-4o": "gpt-4o",
    "GPT-4o Mini": "gpt-4o-mini",
    "GPT-4 Turbo": "gpt-4-turbo",
    "o1-preview": "o1-preview"
}

# Models that require global region (Vertex AI only)
GLOBAL_REGION_MODELS = ["claude-sonnet-4-5@20250929"]

# Default settings
DEFAULT_AUTH_METHOD = "Vertex AI"
DEFAULT_VERTEX_MODEL = "claude-sonnet-4-5@20250929"
DEFAULT_GOOGLE_AI_MODEL = "gemini-2.5-flash"
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 32000  # Increased for complete skill generation with all content

# Vertex AI settings
DEFAULT_VERTEX_LOCATION = "us-central1"

# Skill installation
CLAUDE_SKILLS_DIR = Path.home() / ".claude" / "skills"

# Validation script path (relative to anthropic-skills-reference)
VALIDATION_SCRIPT = BASE_DIR.parent / "anthropic-skills-reference" / "skill-creator" / "scripts" / "quick_validate.py"

# Streamlit configuration
PAGE_TITLE = "Repo-to-Skill Converter"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# UI Constants
MAX_BATCH_SIZE = 5
PROGRESS_STEPS = ["Cloning", "Analyzing", "Generating", "Validating", "Packaging"]

# GitHub API
GITHUB_API_BASE = "https://api.github.com"
