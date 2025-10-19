"""
Skill validation module
Validates skills using Anthropic's validation script
"""
import subprocess
import sys
from pathlib import Path
from typing import Tuple

from config import VALIDATION_SCRIPT


class SkillValidator:
    """Validate Claude Skills"""

    def __init__(self, validation_script: Path = VALIDATION_SCRIPT):
        self.validation_script = validation_script

    def validate_skill(self, skill_dir: Path, progress_callback=None) -> Tuple[bool, str]:
        """
        Validate skill using Anthropic's validation script

        Args:
            skill_dir: Path to skill directory
            progress_callback: Optional callback for progress updates

        Returns:
            (is_valid, message)
        """
        if progress_callback:
            progress_callback("Validating skill...")

        # Check if validation script exists
        if not self.validation_script.exists():
            return self._fallback_validation(skill_dir)

        try:
            # Run validation script
            result = subprocess.run(
                [sys.executable, str(self.validation_script), str(skill_dir)],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Check result
            if result.returncode == 0:
                return True, "Skill is valid!"
            else:
                error_msg = result.stdout + result.stderr
                return False, f"Validation failed: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Validation timed out"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def _fallback_validation(self, skill_dir: Path) -> Tuple[bool, str]:
        """
        Fallback validation if Anthropic's script is not available

        Performs basic structure checks
        """
        errors = []

        # Check SKILL.md exists
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            errors.append("SKILL.md not found")
        else:
            # Validate SKILL.md has frontmatter
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.startswith('---'):
                    errors.append("SKILL.md missing YAML frontmatter")
                else:
                    # Check for required frontmatter fields
                    if 'name:' not in content[:500]:
                        errors.append("SKILL.md missing 'name' in frontmatter")
                    if 'description:' not in content[:500]:
                        errors.append("SKILL.md missing 'description' in frontmatter")

        # Check references directory (optional but recommended)
        references_dir = skill_dir / "references"
        if references_dir.exists():
            if not any(references_dir.iterdir()):
                errors.append("references/ directory is empty")

        # Check templates directory (optional)
        templates_dir = skill_dir / "assets" / "templates"
        if templates_dir.exists():
            if not any(templates_dir.iterdir()):
                errors.append("assets/templates/ directory is empty")

        if errors:
            return False, "Validation errors:\n- " + "\n- ".join(errors)
        else:
            return True, "Skill structure is valid (basic validation)"

    def quick_check(self, skill_dir: Path) -> bool:
        """Quick check if skill has minimum required files"""
        skill_md = skill_dir / "SKILL.md"
        return skill_md.exists()
