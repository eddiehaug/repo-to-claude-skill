"""
Repo-to-Skill Converter
AI-powered Streamlit app to convert GitHub repositories into Claude Skills
"""
import os
import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.repo_analyzer import RepoAnalyzer
from src.ai_generator import create_generator
from src.skill_builder import SkillBuilder
from src.validator import SkillValidator
from src.packager import SkillPackager
from src.database import SkillDatabase
from config import (
    PAGE_TITLE, PAGE_ICON, LAYOUT, MAX_BATCH_SIZE, PROGRESS_STEPS,
    AUTH_METHODS, VERTEX_AI_MODELS, GOOGLE_AI_STUDIO_MODELS,
    ANTHROPIC_API_MODELS, OPENAI_API_MODELS,
    DEFAULT_AUTH_METHOD, DEFAULT_VERTEX_MODEL, DEFAULT_GOOGLE_AI_MODEL,
    DEFAULT_ANTHROPIC_MODEL, DEFAULT_OPENAI_MODEL, DEFAULT_VERTEX_LOCATION,
    GLOBAL_REGION_MODELS, OUTPUT_DIR
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    """Load custom CSS"""
    css_path = Path(__file__).parent / "templates" / "custom_styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
if 'auth_method' not in st.session_state:
    st.session_state.auth_method = DEFAULT_AUTH_METHOD
if 'google_api_key' not in st.session_state:
    st.session_state.google_api_key = os.getenv('GOOGLE_API_KEY', '')
if 'anthropic_api_key' not in st.session_state:
    st.session_state.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = os.getenv('OPENAI_API_KEY', '')
if 'gcp_project_id' not in st.session_state:
    st.session_state.gcp_project_id = os.getenv('GCP_PROJECT_ID', '')
if 'gcp_location' not in st.session_state:
    st.session_state.gcp_location = os.getenv('GCP_LOCATION', DEFAULT_VERTEX_LOCATION)
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = DEFAULT_VERTEX_MODEL
if 'github_token' not in st.session_state:
    st.session_state.github_token = os.getenv('GITHUB_TOKEN', '')
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []
if 'last_generated_skill' not in st.session_state:
    st.session_state.last_generated_skill = None
if 'installation_status' not in st.session_state:
    st.session_state.installation_status = {}


def main():
    """Main application"""

    # Header
    st.title("🤖 Repo-to-Skill Converter")
    st.markdown("*AI-powered tool to convert GitHub repositories into Claude Skills*")

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Authentication method selection
        auth_method = st.selectbox(
            "Authentication Method",
            options=AUTH_METHODS,
            index=AUTH_METHODS.index(st.session_state.auth_method),
            help="Choose your AI provider authentication method"
        )
        st.session_state.auth_method = auth_method

        # Conditional inputs based on auth method
        if auth_method == "Vertex AI":
            # GCP Project ID
            gcp_project_id = st.text_input(
                "GCP Project ID",
                value=st.session_state.gcp_project_id,
                help="Your Google Cloud Project ID"
            )
            st.session_state.gcp_project_id = gcp_project_id

            # GCP Location
            gcp_location = st.text_input(
                "GCP Location",
                value=st.session_state.gcp_location,
                help="Vertex AI location (e.g., us-central1)"
            )
            st.session_state.gcp_location = gcp_location

            # Model selection for Vertex AI
            model_options = list(VERTEX_AI_MODELS.keys())
            selected_model_name = st.selectbox(
                "Model",
                options=model_options,
                index=model_options.index("Claude Sonnet 4.5") if "Claude Sonnet 4.5" in model_options else 0,
                help="Select Gemini or Claude model via Vertex AI"
            )
            st.session_state.selected_model = VERTEX_AI_MODELS[selected_model_name]

            # Show info about authentication and region
            st.info("💡 Make sure you've authenticated with `gcloud auth application-default login`")

            # Show note if Claude model is selected (uses global region)
            if st.session_state.selected_model in GLOBAL_REGION_MODELS:
                st.warning("⚠️ Claude Sonnet uses the 'global' region (location override applied automatically)")

        elif auth_method == "Google AI Studio":
            # Google API Key input
            google_api_key = st.text_input(
                "Google API Key",
                value=st.session_state.google_api_key,
                type="password",
                help="Get your API key from https://aistudio.google.com/apikey"
            )
            st.session_state.google_api_key = google_api_key

            # Model selection for Google AI Studio
            model_options = list(GOOGLE_AI_STUDIO_MODELS.keys())
            selected_model_name = st.selectbox(
                "Model",
                options=model_options,
                index=model_options.index("Gemini 2.5 Flash") if "Gemini 2.5 Flash" in model_options else 0,
                help="Select Gemini model"
            )
            st.session_state.selected_model = GOOGLE_AI_STUDIO_MODELS[selected_model_name]

        elif auth_method == "Anthropic API":
            # Anthropic API Key input
            anthropic_api_key = st.text_input(
                "Anthropic API Key",
                value=st.session_state.anthropic_api_key,
                type="password",
                help="Get your API key from https://console.anthropic.com/"
            )
            st.session_state.anthropic_api_key = anthropic_api_key

            # Model selection for Anthropic API
            model_options = list(ANTHROPIC_API_MODELS.keys())
            selected_model_name = st.selectbox(
                "Model",
                options=model_options,
                index=0,
                help="Select Claude model"
            )
            st.session_state.selected_model = ANTHROPIC_API_MODELS[selected_model_name]

        elif auth_method == "OpenAI API":
            # OpenAI API Key input
            openai_api_key = st.text_input(
                "OpenAI API Key",
                value=st.session_state.openai_api_key,
                type="password",
                help="Get your API key from https://platform.openai.com/api-keys"
            )
            st.session_state.openai_api_key = openai_api_key

            # Model selection for OpenAI API
            model_options = list(OPENAI_API_MODELS.keys())
            selected_model_name = st.selectbox(
                "Model",
                options=model_options,
                index=model_options.index("GPT-4o Mini") if "GPT-4o Mini" in model_options else 0,
                help="Select GPT model"
            )
            st.session_state.selected_model = OPENAI_API_MODELS[selected_model_name]

        st.divider()

        # GitHub token (optional) - common to both methods
        github_token = st.text_input(
            "GitHub Token (Optional)",
            value=st.session_state.github_token,
            type="password",
            help="For higher rate limits. Get from https://github.com/settings/tokens"
        )
        st.session_state.github_token = github_token

        st.divider()

        # Stats
        st.header("📊 Statistics")
        db = SkillDatabase()
        stats = db.get_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Skills", stats['total'])
            st.metric("Successful", stats['successful'])
        with col2:
            st.metric("Failed", stats['failed'])
            st.metric("Installed", stats['installed'])

        st.divider()

        # History
        st.header("📜 History")
        show_history()

    # Main content
    tabs = st.tabs(["✨ Generate", "📚 Batch Generate", "ℹ️ About"])

    with tabs[0]:
        single_generation_ui()

    with tabs[1]:
        batch_generation_ui()

    with tabs[2]:
        about_ui()


def single_generation_ui():
    """UI for single repository conversion"""
    st.header("Generate Skill from Repository")

    # Input
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/owner/repository",
        help="Enter the full GitHub repository URL"
    )

    # Generate button
    col1, col2 = st.columns([1, 4])
    with col1:
        generate_btn = st.button("🚀 Generate Skill", type="primary", use_container_width=True)

    if generate_btn:
        # Validate based on authentication method
        if st.session_state.auth_method == "Vertex AI":
            if not st.session_state.gcp_project_id:
                st.error("⚠️ Please enter your GCP Project ID in the sidebar")
                return
        elif st.session_state.auth_method == "Google AI Studio":
            if not st.session_state.google_api_key:
                st.error("⚠️ Please enter your Google API key in the sidebar")
                return
        elif st.session_state.auth_method == "Anthropic API":
            if not st.session_state.anthropic_api_key:
                st.error("⚠️ Please enter your Anthropic API key in the sidebar")
                return
        elif st.session_state.auth_method == "OpenAI API":
            if not st.session_state.openai_api_key:
                st.error("⚠️ Please enter your OpenAI API key in the sidebar")
                return

        if not repo_url:
            st.error("⚠️ Please enter a repository URL")
            return

        # Clear previous result
        st.session_state.last_generated_skill = None

        # Generate skill
        generate_skill_workflow(repo_url)

    # Show last generated skill if available
    if st.session_state.last_generated_skill:
        show_success_result_persistent(st.session_state.last_generated_skill)


def batch_generation_ui():
    """UI for batch repository conversion"""
    st.header("Batch Generate Skills")

    st.info("💡 Generate skills for multiple repositories at once (max 5)")

    # Text area for URLs
    urls_text = st.text_area(
        "Repository URLs (one per line)",
        height=150,
        placeholder="https://github.com/owner/repo1\nhttps://github.com/owner/repo2\n..."
    )

    # Parse URLs
    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]

    if urls:
        st.info(f"📝 {len(urls)} repository URL{'s' if len(urls) != 1 else ''} entered")

        if len(urls) > MAX_BATCH_SIZE:
            st.warning(f"⚠️ Maximum {MAX_BATCH_SIZE} repositories allowed. Only the first {MAX_BATCH_SIZE} will be processed.")
            urls = urls[:MAX_BATCH_SIZE]

    # Generate button
    if st.button("🚀 Generate All Skills", type="primary"):
        # Validate based on authentication method
        if st.session_state.auth_method == "Vertex AI":
            if not st.session_state.gcp_project_id:
                st.error("⚠️ Please enter your GCP Project ID in the sidebar")
                return
        elif st.session_state.auth_method == "Google AI Studio":
            if not st.session_state.google_api_key:
                st.error("⚠️ Please enter your Google API key in the sidebar")
                return
        elif st.session_state.auth_method == "Anthropic API":
            if not st.session_state.anthropic_api_key:
                st.error("⚠️ Please enter your Anthropic API key in the sidebar")
                return
        elif st.session_state.auth_method == "OpenAI API":
            if not st.session_state.openai_api_key:
                st.error("⚠️ Please enter your OpenAI API key in the sidebar")
                return

        if not urls:
            st.error("⚠️ Please enter at least one repository URL")
            return

        # Generate skills
        batch_generate_workflow(urls)


def generate_skill_workflow(repo_url: str):
    """Workflow for generating a single skill"""
    # Progress container
    progress_container = st.container()

    with progress_container:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Results
        results_container = st.container()

        def update_progress(step_index, message):
            """Update progress bar and message"""
            progress = (step_index + 1) / len(PROGRESS_STEPS)
            progress_bar.progress(progress)
            status_text.text(f"⏳ {PROGRESS_STEPS[step_index]}: {message}")

        try:
            # Initialize components
            analyzer = RepoAnalyzer(st.session_state.github_token)

            # Create AI generator based on authentication method
            if st.session_state.auth_method == "Vertex AI":
                # Use "global" region for Claude models, otherwise use configured location
                location = "global" if st.session_state.selected_model in GLOBAL_REGION_MODELS else st.session_state.gcp_location

                generator = create_generator(
                    auth_method="Vertex AI",
                    project_id=st.session_state.gcp_project_id,
                    location=location,
                    model=st.session_state.selected_model
                )
            elif st.session_state.auth_method == "Google AI Studio":
                generator = create_generator(
                    auth_method="Google AI Studio",
                    api_key=st.session_state.google_api_key,
                    model=st.session_state.selected_model
                )
            elif st.session_state.auth_method == "Anthropic API":
                generator = create_generator(
                    auth_method="Anthropic API",
                    api_key=st.session_state.anthropic_api_key,
                    model=st.session_state.selected_model
                )
            elif st.session_state.auth_method == "OpenAI API":
                generator = create_generator(
                    auth_method="OpenAI API",
                    api_key=st.session_state.openai_api_key,
                    model=st.session_state.selected_model
                )

            builder = SkillBuilder()
            validator = SkillValidator()
            packager = SkillPackager()
            db = SkillDatabase()

            # Step 1: Validate URL
            update_progress(0, "Validating repository URL...")
            is_valid, error = analyzer.validate_github_url(repo_url)
            if not is_valid:
                st.error(f"❌ Invalid URL: {error}")
                return

            repo_info = analyzer.extract_repo_info(repo_url)

            # Fetch metadata
            update_progress(0, "Fetching repository metadata...")
            repo_metadata = analyzer.fetch_repo_metadata(repo_info['owner'], repo_info['repo'])

            if not repo_metadata:
                st.error("❌ Could not fetch repository metadata. Check URL and try again.")
                return

            # Step 2: Clone repository
            update_progress(0, "Cloning repository...")
            repo_path = analyzer.clone_repository(repo_url)

            if not repo_path:
                st.error("❌ Failed to clone repository")
                return

            # Step 3: Analyze repository
            update_progress(1, "Analyzing repository structure...")
            analysis = analyzer.analyze_repository(repo_path)

            # Step 4: Generate skill using AI
            update_progress(2, "Generating skill content with AI...")
            skill_data = generator.generate_skill(
                repo_name=repo_info['full_name'],
                repo_url=repo_url,
                repo_metadata=repo_metadata,
                analysis=analysis
            )

            if not skill_data:
                st.error("❌ Failed to generate skill content")
                analyzer.cleanup(repo_path)
                return

            # Step 5: Build skill structure
            update_progress(3, "Creating skill structure...")
            skill_dir = builder.build_skill(skill_data)

            # Step 6: Validate skill
            update_progress(4, "Validating skill...")
            is_valid, validation_msg = validator.validate_skill(skill_dir)

            if not is_valid:
                st.warning(f"⚠️ Validation issues: {validation_msg}")

            # Step 7: Package skill
            update_progress(4, "Packaging skill...")
            success, zip_path = packager.package_skill(skill_dir)

            if not success:
                st.error("❌ Failed to package skill")
                analyzer.cleanup(repo_path)
                return

            # Cleanup
            analyzer.cleanup(repo_path)

            # Save to database
            skill_name = skill_data['skill_md']['frontmatter']['name']
            description = skill_data['skill_md']['frontmatter']['description']

            db.add_skill(
                skill_name=skill_name,
                repo_url=repo_url,
                repo_name=repo_info['full_name'],
                description=description,
                status="success",
                zip_path=str(zip_path)
            )

            # Store in session state
            st.session_state.last_generated_skill = {
                'skill_name': skill_name,
                'description': description,
                'zip_path': str(zip_path),
                'skill_dir': str(skill_dir)
            }

            # Clear progress
            progress_bar.empty()
            status_text.empty()

            # Show success (will be persisted via session state)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def batch_generate_workflow(urls: list):
    """Workflow for generating multiple skills"""
    st.info(f"🚀 Generating {len(urls)} skills...")

    results = []

    for i, url in enumerate(urls):
        with st.expander(f"📦 Repository {i+1}/{len(urls)}: {url}", expanded=True):
            generate_skill_workflow(url)

        time.sleep(1)  # Brief delay between generations


def show_success_result_persistent(skill_info):
    """Show success message and installation options with persistent state"""
    skill_name = skill_info['skill_name']
    description = skill_info['description']
    zip_path = Path(skill_info['zip_path'])
    skill_dir = Path(skill_info['skill_dir'])

    st.success("✅ Skill generated successfully!")

    # Skill info
    st.subheader(f"📚 {skill_name}")
    st.write(description)

    st.divider()

    # Installation options
    st.subheader("📥 Installation")

    col1, col2 = st.columns(2)

    with col1:
        # Check if already installed
        packager = SkillPackager()
        is_installed = packager.is_skill_installed(skill_name)

        if is_installed:
            st.success("✅ Skill is already installed")
            if st.button("🔄 Reinstall", key=f"reinstall_{skill_name}"):
                with st.spinner("Reinstalling skill..."):
                    success, message = packager.install_skill(skill_dir)
                    if success:
                        st.success(f"✅ {message}")
                        # Update database
                        db = SkillDatabase()
                        skills = db.search_skills(skill_name)
                        if skills:
                            db.update_skill(skills[0]['id'], installed=True)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        else:
            if st.button("✨ Install to Claude Skills", key=f"install_{skill_name}"):
                with st.spinner("Installing skill..."):
                    success, message = packager.install_skill(skill_dir)
                    if success:
                        st.success(f"✅ {message}")
                        # Update database
                        db = SkillDatabase()
                        skills = db.search_skills(skill_name)
                        if skills:
                            db.update_skill(skills[0]['id'], installed=True)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

    with col2:
        if zip_path.exists():
            with open(zip_path, 'rb') as f:
                st.download_button(
                    label="💾 Download ZIP",
                    data=f,
                    file_name=f"{skill_name}.zip",
                    mime="application/zip",
                    key=f"download_{skill_name}"
                )


def show_success_result(skill_name, description, zip_path, skill_dir, container):
    """Show success message and installation options (legacy for batch mode)"""
    with container:
        st.success("✅ Skill generated successfully!")

        # Skill info
        st.subheader(f"📚 {skill_name}")
        st.write(description)

        st.divider()

        # Installation options
        st.subheader("📥 Installation")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✨ Install to Claude Skills", key=f"install_{skill_name}"):
                with st.spinner("Installing skill..."):
                    packager = SkillPackager()
                    success, message = packager.install_skill(skill_dir)

                    if success:
                        st.success(f"✅ {message}")

                        # Update database
                        db = SkillDatabase()
                        # Find skill by name and update
                        skills = db.search_skills(skill_name)
                        if skills:
                            db.update_skill(skills[0]['id'], installed=True)
                    else:
                        st.error(f"❌ {message}")

        with col2:
            with open(zip_path, 'rb') as f:
                st.download_button(
                    label="💾 Download ZIP",
                    data=f,
                    file_name=f"{skill_name}.zip",
                    mime="application/zip",
                    key=f"download_{skill_name}"
                )


def show_history():
    """Show skill generation history"""
    db = SkillDatabase()
    skills = db.get_all_skills(limit=10)

    if not skills:
        st.info("No skills generated yet")
        return

    for skill in skills:
        status_icon = "✅" if skill['status'] == 'success' else "❌"

        with st.expander(f"{status_icon} {skill['skill_name']}", expanded=False):
            st.text(f"Repository: {skill['repo_url']}")
            st.text(f"Created: {skill['created_at']}")

            if skill['status'] == 'success' and skill['zip_path']:
                zip_path = Path(skill['zip_path'])

                # Check if skill is installed
                packager = SkillPackager()
                is_installed = packager.is_skill_installed(skill['skill_name'])

                if is_installed:
                    st.success("✅ Installed")
                else:
                    st.warning("⚠️ Not installed")

                # Find skill directory
                skill_dir = OUTPUT_DIR / skill['skill_name']

                col1, col2 = st.columns(2)

                with col1:
                    if zip_path.exists():
                        with open(zip_path, 'rb') as f:
                            st.download_button(
                                label="💾 Download",
                                data=f,
                                file_name=zip_path.name,
                                mime="application/zip",
                                key=f"hist_download_{skill['id']}"
                            )

                with col2:
                    if skill_dir.exists():
                        if is_installed:
                            if st.button("🔄 Reinstall", key=f"hist_reinstall_{skill['id']}"):
                                with st.spinner("Reinstalling..."):
                                    success, message = packager.install_skill(skill_dir)
                                    if success:
                                        st.success("✅ Reinstalled!")
                                        db.update_skill(skill['id'], installed=True)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
                        else:
                            if st.button("✨ Install", key=f"hist_install_{skill['id']}"):
                                with st.spinner("Installing..."):
                                    success, message = packager.install_skill(skill_dir)
                                    if success:
                                        st.success("✅ Installed!")
                                        db.update_skill(skill['id'], installed=True)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")


def about_ui():
    """About page"""
    st.header("About Repo-to-Skill Converter")

    st.markdown("""
    ## What is this?

    The **Repo-to-Skill Converter** is an AI-powered tool that automatically converts GitHub repositories
    into comprehensive Claude Skills.

    ## How it works

    1. **Clone**: Downloads the repository to analyze its structure
    2. **Analyze**: Examines README, code samples, file structure, and documentation
    3. **Generate**: Uses Claude AI to create comprehensive skill documentation following Anthropic's best practices
    4. **Validate**: Checks skill structure for correctness
    5. **Package**: Creates a .zip file ready for installation

    ## Features

    ✅ **AI-Powered Analysis**: Uses Claude Sonnet to understand repositories and create meaningful documentation

    ✅ **Batch Processing**: Convert multiple repositories at once

    ✅ **Automatic Validation**: Ensures skills meet Anthropic's standards

    ✅ **One-Click Installation**: Install directly to `~/.claude/skills/` directory

    ✅ **History Tracking**: Keep track of all generated skills

    ## Requirements

    - Claude API Key ([Get one here](https://console.anthropic.com/))
    - GitHub repository URL (public repositories)
    - Optional: GitHub Personal Access Token for higher rate limits

    ## Claude Skills

    Learn more about Claude Skills:
    - [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
    - [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
    - [Creating Custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)

    ---

    **Version**: 1.0.0 | Built with Streamlit and Claude AI
    """)


if __name__ == "__main__":
    main()
