"""
AI-powered skill generation using Claude API or Vertex AI
"""
import json
from typing import Dict, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from config import MAX_TOKENS, TEMPLATES_DIR


class BaseSkillGenerator(ABC):
    """Base class for skill generators"""

    def __init__(self):
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load skill generation prompt template"""
        prompt_path = TEMPLATES_DIR / "skill_prompt.txt"

        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading prompt template: {e}")
            return ""

    @abstractmethod
    def _call_ai_api(self, prompt: str, progress_callback=None) -> Optional[str]:
        """Call the AI API - implemented by subclasses"""
        pass

    def generate_skill(
        self,
        repo_name: str,
        repo_url: str,
        repo_metadata: Dict,
        analysis: Dict,
        progress_callback=None
    ) -> Optional[Dict]:
        """
        Generate skill content using AI

        Args:
            repo_name: Repository full name (owner/repo)
            repo_url: Repository URL
            repo_metadata: GitHub API metadata
            analysis: Repository analysis results
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with skill content or None if error
        """
        if progress_callback:
            progress_callback("Preparing data for AI generation...")

        # Prepare prompt
        prompt = self._prepare_prompt(
            repo_name=repo_name,
            repo_url=repo_url,
            repo_metadata=repo_metadata,
            analysis=analysis
        )

        try:
            if progress_callback:
                progress_callback("Calling AI API to generate skill...")

            # Call AI API (implemented by subclass)
            response_text = self._call_ai_api(prompt, progress_callback)

            if not response_text:
                return None

            if progress_callback:
                progress_callback("Parsing AI response...")

            # Parse JSON response
            skill_data = self._parse_response(response_text)

            return skill_data

        except Exception as e:
            print(f"Error generating skill: {e}")
            return None

    def _prepare_prompt(
        self,
        repo_name: str,
        repo_url: str,
        repo_metadata: Dict,
        analysis: Dict
    ) -> str:
        """Prepare the prompt for AI API"""

        # Format code samples
        code_samples_text = ""
        if analysis.get('code_samples'):
            for i, sample in enumerate(analysis['code_samples'][:3], 1):
                code_samples_text += f"\n## Sample {i}: {sample['file']}\n\n"
                code_samples_text += f"```{sample['language']}\n{sample['content']}\n```\n"
        else:
            code_samples_text = "No code samples available"

        # Format file structure
        file_structure_text = ""
        if analysis.get('file_structure'):
            for name, type_info in list(analysis['file_structure'].items())[:20]:
                file_structure_text += f"- {name} ({type_info})\n"
        else:
            file_structure_text = "File structure not available"

        # Fill in template
        prompt = self.prompt_template.format(
            repo_name=repo_name,
            repo_url=repo_url,
            repo_type=analysis.get('repo_type', 'unknown'),
            languages=', '.join(analysis.get('languages', ['Unknown'])),
            repo_description=repo_metadata.get('description', 'No description available'),
            readme_content=analysis.get('readme_content', 'README not found')[:8000],  # Limit size
            file_structure=file_structure_text,
            code_samples=code_samples_text
        )

        return prompt

    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse AI's JSON response

        Returns:
            Parsed skill data or None if parsing fails
        """
        try:
            # Extract JSON from response (may be wrapped in markdown code blocks)
            if "```json" in response_text:
                # Extract from code block
                start = response_text.find("```json") + 7
                end = response_text.rfind("```")
                json_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Generic code block
                start = response_text.find("```") + 3
                end = response_text.rfind("```")
                json_text = response_text[start:end].strip()
            else:
                # Assume entire response is JSON
                json_text = response_text.strip()

            # Parse JSON
            skill_data = json.loads(json_text)

            # Validate structure
            if not self._validate_skill_data(skill_data):
                print("Invalid skill data structure")
                return None

            return skill_data

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text[:500]}")
            return None

    def _validate_skill_data(self, data: Dict) -> bool:
        """Validate that skill data has required structure"""
        required_keys = ['skill_md', 'references', 'templates']

        if not all(key in data for key in required_keys):
            return False

        # Validate skill_md structure
        skill_md = data.get('skill_md', {})
        if not isinstance(skill_md, dict):
            return False

        if 'frontmatter' not in skill_md or 'content' not in skill_md:
            return False

        frontmatter = skill_md.get('frontmatter', {})
        if 'name' not in frontmatter or 'description' not in frontmatter:
            return False

        # Validate references and templates are lists
        if not isinstance(data.get('references'), list):
            return False

        if not isinstance(data.get('templates'), list):
            return False

        return True


class ClaudeAPIGenerator(BaseSkillGenerator):
    """Skill generator using Claude API"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__()
        self.model = model
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)

    def _call_ai_api(self, prompt: str, progress_callback=None) -> Optional[str]:
        """Call Claude API with streaming"""
        try:
            print(f"[DEBUG] Calling Claude API ({self.model}) with max_tokens={MAX_TOKENS} (streaming)")

            response_text = ""

            with self.client.messages.stream(
                model=self.model,
                max_tokens=MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            ) as stream:
                for text in stream.text_stream:
                    response_text += text

                    # Optional: Update progress callback
                    if progress_callback and len(response_text) % 1000 == 0:
                        progress_callback(f"Generating... ({len(response_text)} chars)")

                # Get final message for metadata
                message = stream.get_final_message()

            # Debug logging
            print(f"[DEBUG] Response length: {len(response_text)} characters")
            print(f"[DEBUG] Stop reason: {message.stop_reason}")

            return response_text

        except Exception as e:
            print(f"Claude API error: {e}")
            import traceback
            traceback.print_exc()
            return None


class VertexAIGenerator(BaseSkillGenerator):
    """Skill generator using Vertex AI (Gemini or Claude models)"""

    def __init__(self, project_id: str, location: str, model: str):
        super().__init__()
        self.project_id = project_id
        self.location = location
        self.model = model
        self.is_claude = "claude" in model.lower()

        # Initialize appropriate client based on model type
        if self.is_claude:
            # Use Anthropic SDK for Claude models on Vertex AI
            try:
                import anthropic
                self.client = anthropic.AnthropicVertex(
                    project_id=project_id,
                    region=location
                )
            except Exception as e:
                print(f"Error initializing Anthropic Vertex AI: {e}")
                raise
        else:
            # Use Google GenAI SDK for Gemini models
            try:
                from google import genai
                self.client = genai.Client(
                    vertexai=True,
                    project=project_id,
                    location=location
                )
            except Exception as e:
                print(f"Error initializing Vertex AI: {e}")
                raise

    def _call_ai_api(self, prompt: str, progress_callback=None) -> Optional[str]:
        """Call Vertex AI (Gemini or Claude)"""
        try:
            if self.is_claude:
                # Call Claude via Anthropic Vertex AI with streaming
                print(f"[DEBUG] Calling Claude with max_tokens={MAX_TOKENS} (streaming)")

                response_text = ""

                with self.client.messages.stream(
                    model=self.model,
                    max_tokens=MAX_TOKENS,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                ) as stream:
                    for text in stream.text_stream:
                        response_text += text

                        # Optional: Update progress callback with partial response
                        if progress_callback and len(response_text) % 1000 == 0:
                            progress_callback(f"Generating... ({len(response_text)} chars)")

                    # Get final message for metadata
                    message = stream.get_final_message()

                # Debug logging
                print(f"[DEBUG] Response length: {len(response_text)} characters")
                print(f"[DEBUG] Stop reason: {message.stop_reason}")

                return response_text

            else:
                # Call Gemini via Google GenAI
                print(f"[DEBUG] Calling Gemini with max_tokens={MAX_TOKENS}")
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "max_output_tokens": MAX_TOKENS,
                        "temperature": 0.7,
                    }
                )

                # Extract text from response
                if response and response.text:
                    response_text = response.text
                    print(f"[DEBUG] Response length: {len(response_text)} characters")

                    return response_text
                else:
                    print("Empty response from Vertex AI")
                    return None

        except Exception as e:
            print(f"Vertex AI error: {e}")
            import traceback
            traceback.print_exc()
            return None


class GoogleAIStudioGenerator(BaseSkillGenerator):
    """Skill generator using Google AI Studio API (Gemini models)"""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        super().__init__()
        self.api_key = api_key
        self.model = model

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai
        except Exception as e:
            print(f"Error initializing Google AI Studio: {e}")
            raise

    def _call_ai_api(self, prompt: str, progress_callback=None) -> Optional[str]:
        """Call Google AI Studio API"""
        try:
            print(f"[DEBUG] Calling Google AI Studio ({self.model}) with max_tokens={MAX_TOKENS}")

            # Create model instance
            model = self.client.GenerativeModel(self.model)

            # Generate content
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": MAX_TOKENS,
                    "temperature": 0.7,
                }
            )

            response_text = response.text
            print(f"[DEBUG] Response length: {len(response_text)} characters")

            return response_text

        except Exception as e:
            print(f"Google AI Studio error: {e}")
            import traceback
            traceback.print_exc()
            return None


class OpenAIGenerator(BaseSkillGenerator):
    """Skill generator using OpenAI API (GPT models)"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__()
        self.model = model

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"Error initializing OpenAI: {e}")
            raise

    def _call_ai_api(self, prompt: str, progress_callback=None) -> Optional[str]:
        """Call OpenAI API with streaming"""
        try:
            print(f"[DEBUG] Calling OpenAI ({self.model}) with max_tokens={MAX_TOKENS}")

            response_text = ""

            # Use streaming for long responses
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_completion_tokens=MAX_TOKENS,
                temperature=0.7,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content

                    # Optional: Update progress callback
                    if progress_callback and len(response_text) % 1000 == 0:
                        progress_callback(f"Generating... ({len(response_text)} chars)")

            print(f"[DEBUG] Response length: {len(response_text)} characters")

            return response_text

        except Exception as e:
            print(f"OpenAI error: {e}")
            import traceback
            traceback.print_exc()
            return None


def create_generator(auth_method: str, **kwargs) -> BaseSkillGenerator:
    """
    Factory function to create appropriate skill generator

    Args:
        auth_method: Authentication method (Vertex AI, Google AI Studio, Anthropic API, OpenAI API)
        **kwargs: Authentication parameters
            For Vertex AI: project_id, location, model
            For Google AI Studio: api_key, model
            For Anthropic API: api_key, model
            For OpenAI API: api_key, model

    Returns:
        Appropriate skill generator instance
    """
    if auth_method == "Vertex AI":
        project_id = kwargs.get('project_id')
        location = kwargs.get('location', 'us-central1')
        model = kwargs.get('model', 'claude-sonnet-4-5@20250929')

        if not project_id:
            raise ValueError("Project ID required for Vertex AI")

        return VertexAIGenerator(project_id, location, model)

    elif auth_method == "Google AI Studio":
        api_key = kwargs.get('api_key')
        model = kwargs.get('model', 'gemini-2.5-flash')

        if not api_key:
            raise ValueError("API key required for Google AI Studio")

        return GoogleAIStudioGenerator(api_key, model)

    elif auth_method == "Anthropic API":
        api_key = kwargs.get('api_key')
        model = kwargs.get('model', 'claude-3-5-sonnet-20241022')

        if not api_key:
            raise ValueError("API key required for Anthropic API")

        return ClaudeAPIGenerator(api_key, model)

    elif auth_method == "OpenAI API":
        api_key = kwargs.get('api_key')
        model = kwargs.get('model', 'gpt-4o-mini')

        if not api_key:
            raise ValueError("API key required for OpenAI API")

        return OpenAIGenerator(api_key, model)

    else:
        raise ValueError(f"Unknown authentication method: {auth_method}")
