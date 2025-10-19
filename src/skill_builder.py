"""
Skill builder module
Creates skill folder structure from AI-generated content
"""
from pathlib import Path
from typing import Dict
import yaml

from config import OUTPUT_DIR


class SkillBuilder:
    """Build Claude Skill folder structure"""

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir

    def build_skill(self, skill_data: Dict, progress_callback=None) -> Path:
        """
        Build skill folder structure from AI-generated data

        Args:
            skill_data: Dictionary with skill content from AI generator
            progress_callback: Optional callback for progress updates

        Returns:
            Path to created skill directory
        """
        if progress_callback:
            progress_callback("Creating skill structure...")

        # Get skill name
        skill_name = skill_data['skill_md']['frontmatter']['name']

        # Create skill directory
        skill_dir = self.output_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create SKILL.md
            if progress_callback:
                progress_callback("Writing SKILL.md...")
            self._create_skill_md(skill_dir, skill_data['skill_md'])

            # Create references
            if skill_data.get('references'):
                if progress_callback:
                    progress_callback("Creating reference documentation...")
                self._create_references(skill_dir, skill_data['references'])

            # Create templates
            if skill_data.get('templates'):
                if progress_callback:
                    progress_callback("Creating code templates...")
                self._create_templates(skill_dir, skill_data['templates'])

            if progress_callback:
                progress_callback("Skill structure created successfully")

            return skill_dir

        except Exception as e:
            print(f"Error building skill: {e}")
            raise

    def _create_skill_md(self, skill_dir: Path, skill_md_data: Dict):
        """Create SKILL.md file with YAML frontmatter"""
        skill_md_path = skill_dir / "SKILL.md"

        # Prepare YAML frontmatter
        frontmatter = skill_md_data['frontmatter']
        yaml_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

        # Combine frontmatter and content
        full_content = f"---\n{yaml_content}---\n\n{skill_md_data['content']}"

        # Write file
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

    def _create_references(self, skill_dir: Path, references: list):
        """Create reference documentation files"""
        references_dir = skill_dir / "references"
        references_dir.mkdir(exist_ok=True)

        for ref in references:
            filename = ref['filename']
            content = ref['content']

            ref_path = references_dir / filename

            with open(ref_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def _create_templates(self, skill_dir: Path, templates: list):
        """Create code template files"""
        templates_dir = skill_dir / "assets" / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)

        for template in templates:
            filename = template['filename']
            content = template['content']

            template_path = templates_dir / filename

            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def get_skill_info(self, skill_dir: Path) -> Dict:
        """
        Extract skill information from SKILL.md

        Returns:
            Dictionary with skill metadata
        """
        skill_md_path = skill_dir / "SKILL.md"

        if not skill_md_path.exists():
            return {}

        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_text = parts[1].strip()
                    frontmatter = yaml.safe_load(frontmatter_text)
                    return frontmatter

        except Exception as e:
            print(f"Error reading skill info: {e}")

        return {}

    def cleanup_skill(self, skill_dir: Path):
        """Remove skill directory"""
        if skill_dir and skill_dir.exists():
            import shutil
            try:
                shutil.rmtree(skill_dir)
            except Exception as e:
                print(f"Error cleaning up skill: {e}")
