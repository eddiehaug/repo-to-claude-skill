"""
Repository analysis module
Handles cloning and analyzing GitHub repositories
"""
import os
import shutil
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import git
import requests

from config import TEMP_DIR, GITHUB_API_BASE


class RepoAnalyzer:
    """Analyze GitHub repositories for skill generation"""

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.headers = {}
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'

    def validate_github_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate if URL is a valid GitHub repository URL

        Returns:
            (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"

        # Security: Prevent excessively long URLs
        if len(url) > 500:
            return False, "URL is too long"

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception:
            return False, "Invalid URL format"

        # Security: Only allow HTTPS protocol (GitHub supports HTTPS for all repos)
        if parsed.scheme != 'https':
            return False, "URL must use HTTPS protocol"

        # Check if it's a GitHub URL
        if parsed.netloc not in ['github.com', 'www.github.com']:
            return False, "URL must be a GitHub repository"

        # Extract owner and repo from path
        path_parts = parsed.path.strip('/').split('/')

        if len(path_parts) < 2:
            return False, "Invalid GitHub repository URL format"

        # Security: Validate owner and repo names (alphanumeric, hyphens, underscores only)
        owner, repo = path_parts[0], path_parts[1].replace('.git', '')

        if not re.match(r'^[a-zA-Z0-9_-]+$', owner):
            return False, "Invalid repository owner name"

        if not re.match(r'^[a-zA-Z0-9_.-]+$', repo):
            return False, "Invalid repository name"

        return True, ""

    def extract_repo_info(self, url: str) -> Dict[str, str]:
        """
        Extract repository owner and name from GitHub URL

        Returns:
            {'owner': str, 'repo': str, 'full_name': str}
        """
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        # Handle URLs with .git extension
        repo_name = path_parts[1].replace('.git', '')

        return {
            'owner': path_parts[0],
            'repo': repo_name,
            'full_name': f"{path_parts[0]}/{repo_name}"
        }

    def fetch_repo_metadata(self, owner: str, repo: str) -> Optional[Dict]:
        """
        Fetch repository metadata from GitHub API

        Returns:
            Repository metadata or None if error
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching repo metadata: {e}")
            return None

    def clone_repository(self, repo_url: str, progress_callback=None) -> Optional[Path]:
        """
        Clone repository to temp directory

        Args:
            repo_url: GitHub repository URL
            progress_callback: Optional callback for progress updates

        Returns:
            Path to cloned repository or None if error
        """
        # Security: Validate URL before cloning
        is_valid, error = self.validate_github_url(repo_url)
        if not is_valid:
            print(f"Invalid repository URL: {error}")
            return None

        repo_info = self.extract_repo_info(repo_url)

        # Security: Sanitize path to prevent directory traversal
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', repo_info['full_name'])
        clone_path = TEMP_DIR / safe_name

        # Security: Ensure clone path is within TEMP_DIR
        try:
            clone_path = clone_path.resolve()
            if not str(clone_path).startswith(str(TEMP_DIR.resolve())):
                print("Security: Attempted path traversal detected")
                return None
        except Exception as e:
            print(f"Error resolving clone path: {e}")
            return None

        # Remove existing clone if present
        if clone_path.exists():
            try:
                shutil.rmtree(clone_path)
            except Exception as e:
                print(f"Error removing existing clone: {e}")
                return None

        try:
            if progress_callback:
                progress_callback("Cloning repository...")

            # Security: Clone with depth=1 and no submodules to limit size
            git.Repo.clone_from(
                repo_url,
                clone_path,
                depth=1,
                no_single_branch=False,
                recurse_submodules=False,
                progress=self._git_progress_callback(progress_callback) if progress_callback else None
            )

            # Security: Check repository size after cloning
            total_size = sum(f.stat().st_size for f in clone_path.rglob('*') if f.is_file())
            max_size = 500 * 1024 * 1024  # 500 MB limit
            if total_size > max_size:
                print(f"Repository too large: {total_size / 1024 / 1024:.2f} MB")
                shutil.rmtree(clone_path)
                return None

            return clone_path

        except git.GitCommandError as e:
            print(f"Error cloning repository: {e}")
            if clone_path.exists():
                shutil.rmtree(clone_path)
            return None
        except Exception as e:
            print(f"Unexpected error during clone: {e}")
            if clone_path.exists():
                shutil.rmtree(clone_path)
            return None

    def _git_progress_callback(self, progress_callback):
        """Create git progress handler"""
        class ProgressHandler(git.RemoteProgress):
            def update(self, op_code, cur_count, max_count=None, message=''):
                if progress_callback and message:
                    progress_callback(f"Cloning: {message}")

        return ProgressHandler()

    def analyze_repository(self, repo_path: Path) -> Dict:
        """
        Analyze repository structure and extract key information

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'readme_content': self._extract_readme(repo_path),
            'file_structure': self._get_file_structure(repo_path),
            'code_samples': self._extract_code_samples(repo_path),
            'repo_type': self._detect_repo_type(repo_path),
            'languages': self._detect_languages(repo_path),
            'has_documentation': self._has_documentation(repo_path),
            'total_files': self._count_files(repo_path),
        }

        return analysis

    def _extract_readme(self, repo_path: Path) -> str:
        """Extract README content"""
        readme_patterns = ['README.md', 'README.rst', 'README.txt', 'README']
        max_size = 1024 * 1024  # 1 MB limit for README

        for pattern in readme_patterns:
            readme_path = repo_path / pattern
            if readme_path.exists():
                try:
                    # Security: Check file size before reading
                    if readme_path.stat().st_size > max_size:
                        print(f"README file too large: {readme_path.stat().st_size / 1024:.2f} KB")
                        continue

                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading README: {e}")

        return ""

    def _get_file_structure(self, repo_path: Path, max_depth: int = 3) -> Dict:
        """Get repository file structure"""
        structure = {}

        try:
            for item in repo_path.iterdir():
                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    structure[item.name] = "directory"
                else:
                    structure[item.name] = item.suffix or "file"

        except Exception as e:
            print(f"Error getting file structure: {e}")

        return structure

    def _extract_code_samples(self, repo_path: Path, max_samples: int = 5) -> list:
        """Extract code samples from repository"""
        code_extensions = ['.py', '.js', '.java', '.go', '.rs', '.ts', '.tsx']
        samples = []
        max_file_size = 100 * 1024  # 100 KB limit for code samples

        try:
            for ext in code_extensions:
                files = list(repo_path.rglob(f"*{ext}"))[:max_samples * 2]  # Get more to filter from

                for file_path in files:
                    # Security: Skip test files, large files, and hidden files
                    if 'test' in str(file_path).lower():
                        continue

                    # Skip hidden files and directories
                    if any(part.startswith('.') for part in file_path.parts):
                        continue

                    try:
                        file_size = file_path.stat().st_size
                        if file_size > max_file_size or file_size == 0:
                            continue

                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(5000)  # Read max 5000 chars
                            samples.append({
                                'file': str(file_path.relative_to(repo_path)),
                                'language': ext[1:],
                                'content': content[:2000]  # First 2000 chars
                            })

                        if len(samples) >= max_samples:
                            break
                    except Exception:
                        continue

                if len(samples) >= max_samples:
                    break

        except Exception as e:
            print(f"Error extracting code samples: {e}")

        return samples

    def _detect_repo_type(self, repo_path: Path) -> str:
        """Detect type of repository"""
        # Check for common indicators
        if (repo_path / 'setup.py').exists() or (repo_path / 'pyproject.toml').exists():
            return 'python_package'

        if (repo_path / 'package.json').exists():
            return 'nodejs_package'

        if (repo_path / 'Cargo.toml').exists():
            return 'rust_package'

        if (repo_path / 'go.mod').exists():
            return 'go_module'

        if list(repo_path.glob('*.framework')) or list(repo_path.glob('*.xcodeproj')):
            return 'ios_framework'

        # Check for documentation sites
        if (repo_path / 'docs').exists() and (repo_path / 'mkdocs.yml').exists():
            return 'documentation'

        # Check for examples/samples
        if 'example' in repo_path.name.lower() or 'sample' in repo_path.name.lower():
            return 'examples'

        return 'library'

    def _detect_languages(self, repo_path: Path) -> list:
        """Detect programming languages used"""
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }

        found_languages = set()

        try:
            for ext, lang in extensions.items():
                if list(repo_path.rglob(f"*{ext}")):
                    found_languages.add(lang)

        except Exception as e:
            print(f"Error detecting languages: {e}")

        return list(found_languages)

    def _has_documentation(self, repo_path: Path) -> bool:
        """Check if repository has documentation"""
        doc_indicators = ['docs/', 'documentation/', 'wiki/', 'API.md', 'USAGE.md']

        for indicator in doc_indicators:
            if (repo_path / indicator).exists():
                return True

        return False

    def _count_files(self, repo_path: Path) -> int:
        """Count total files in repository"""
        try:
            return sum(1 for _ in repo_path.rglob('*') if _.is_file())
        except Exception:
            return 0

    def cleanup(self, repo_path: Path):
        """Clean up cloned repository"""
        if repo_path and repo_path.exists():
            try:
                shutil.rmtree(repo_path)
            except Exception as e:
                print(f"Error cleaning up repository: {e}")
