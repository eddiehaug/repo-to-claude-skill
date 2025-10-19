"""
Skill packaging and installation module
"""
import shutil
import zipfile
from pathlib import Path
from typing import Tuple

from config import OUTPUT_DIR, CLAUDE_SKILLS_DIR


class SkillPackager:
    """Package and install Claude Skills"""

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir

    def package_skill(self, skill_dir: Path, progress_callback=None) -> Tuple[bool, Path]:
        """
        Package skill to .zip file

        Args:
            skill_dir: Path to skill directory
            progress_callback: Optional callback for progress updates

        Returns:
            (success, zip_path)
        """
        if progress_callback:
            progress_callback("Packaging skill...")

        skill_name = skill_dir.name
        zip_path = self.output_dir / f"{skill_name}.zip"

        try:
            # Remove existing zip if present
            if zip_path.exists():
                zip_path.unlink()

            # Create zip file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from skill directory
                for file_path in skill_dir.rglob('*'):
                    if file_path.is_file():
                        # Calculate relative path from skill directory
                        arcname = file_path.relative_to(skill_dir.parent)
                        zipf.write(file_path, arcname)

                        if progress_callback:
                            progress_callback(f"Adding {arcname}...")

            if progress_callback:
                progress_callback(f"Skill packaged to {zip_path.name}")

            return True, zip_path

        except Exception as e:
            print(f"Error packaging skill: {e}")
            return False, None

    def install_skill(
        self,
        skill_dir: Path,
        claude_skills_dir: Path = CLAUDE_SKILLS_DIR,
        progress_callback=None
    ) -> Tuple[bool, str]:
        """
        Install skill to Claude skills directory

        Args:
            skill_dir: Path to skill directory
            claude_skills_dir: Path to Claude skills installation directory
            progress_callback: Optional callback for progress updates

        Returns:
            (success, message)
        """
        if progress_callback:
            progress_callback("Installing skill...")

        skill_name = skill_dir.name
        install_path = claude_skills_dir / skill_name

        try:
            # Create Claude skills directory if it doesn't exist
            claude_skills_dir.mkdir(parents=True, exist_ok=True)

            # Remove existing installation if present
            if install_path.exists():
                shutil.rmtree(install_path)

                if progress_callback:
                    progress_callback("Removed existing installation...")

            # Copy skill directory
            shutil.copytree(skill_dir, install_path)

            if progress_callback:
                progress_callback(f"Skill installed to {install_path}")

            return True, f"Skill installed successfully to {install_path}"

        except PermissionError:
            error_msg = f"Permission denied. Cannot write to {claude_skills_dir}"
            return False, error_msg
        except Exception as e:
            error_msg = f"Installation error: {str(e)}"
            return False, error_msg

    def uninstall_skill(
        self,
        skill_name: str,
        claude_skills_dir: Path = CLAUDE_SKILLS_DIR
    ) -> Tuple[bool, str]:
        """
        Uninstall skill from Claude skills directory

        Args:
            skill_name: Name of skill to uninstall
            claude_skills_dir: Path to Claude skills installation directory

        Returns:
            (success, message)
        """
        install_path = claude_skills_dir / skill_name

        if not install_path.exists():
            return False, f"Skill '{skill_name}' is not installed"

        try:
            shutil.rmtree(install_path)
            return True, f"Skill '{skill_name}' uninstalled successfully"

        except Exception as e:
            return False, f"Error uninstalling skill: {str(e)}"

    def is_skill_installed(
        self,
        skill_name: str,
        claude_skills_dir: Path = CLAUDE_SKILLS_DIR
    ) -> bool:
        """Check if skill is already installed"""
        install_path = claude_skills_dir / skill_name
        return install_path.exists() and (install_path / "SKILL.md").exists()

    def get_zip_download_path(self, skill_name: str) -> Path:
        """Get path to packaged zip file"""
        return self.output_dir / f"{skill_name}.zip"
