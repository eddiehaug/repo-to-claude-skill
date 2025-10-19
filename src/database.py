"""
Database module for storing skill generation history
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json

from config import DATABASE_PATH


class SkillDatabase:
    """Manage skill generation history in SQLite database"""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    repo_url TEXT NOT NULL,
                    repo_name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    zip_path TEXT,
                    installed BOOLEAN DEFAULT 0,
                    metadata TEXT
                )
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_repo_url
                ON skills(repo_url)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON skills(created_at DESC)
            ''')

            conn.commit()

    def add_skill(
        self,
        skill_name: str,
        repo_url: str,
        repo_name: str,
        description: str = "",
        status: str = "pending",
        error_message: Optional[str] = None,
        zip_path: Optional[str] = None,
        installed: bool = False,
        metadata: Optional[Dict] = None
    ) -> int:
        """Add a new skill to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO skills (
                    skill_name, repo_url, repo_name, description,
                    status, error_message, zip_path, installed, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                skill_name,
                repo_url,
                repo_name,
                description,
                status,
                error_message,
                zip_path,
                installed,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
            return cursor.lastrowid

    def update_skill(
        self,
        skill_id: int,
        status: Optional[str] = None,
        error_message: Optional[str] = None,
        zip_path: Optional[str] = None,
        installed: Optional[bool] = None,
        description: Optional[str] = None
    ):
        """Update a skill record"""
        updates = []
        params = []

        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if error_message is not None:
            updates.append("error_message = ?")
            params.append(error_message)

        if zip_path is not None:
            updates.append("zip_path = ?")
            params.append(zip_path)

        if installed is not None:
            updates.append("installed = ?")
            params.append(installed)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if not updates:
            return

        params.append(skill_id)
        query = f"UPDATE skills SET {', '.join(updates)} WHERE id = ?"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def get_skill(self, skill_id: int) -> Optional[Dict]:
        """Get a specific skill by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM skills WHERE id = ?', (skill_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def get_all_skills(self, limit: int = 100) -> List[Dict]:
        """Get all skills, ordered by most recent first"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM skills
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_skills_by_status(self, status: str) -> List[Dict]:
        """Get skills filtered by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM skills
                WHERE status = ?
                ORDER BY created_at DESC
            ''', (status,))

            return [dict(row) for row in cursor.fetchall()]

    def search_skills(self, search_term: str) -> List[Dict]:
        """Search skills by name or repo URL"""
        search_pattern = f"%{search_term}%"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM skills
                WHERE skill_name LIKE ? OR repo_url LIKE ?
                ORDER BY created_at DESC
            ''', (search_pattern, search_pattern))

            return [dict(row) for row in cursor.fetchall()]

    def delete_skill(self, skill_id: int):
        """Delete a skill from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
            conn.commit()

    def get_stats(self) -> Dict:
        """Get statistics about skill generation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM skills')
            total = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM skills WHERE status = "success"')
            successful = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM skills WHERE status = "failed"')
            failed = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM skills WHERE installed = 1')
            installed = cursor.fetchone()[0]

            return {
                'total': total,
                'successful': successful,
                'failed': failed,
                'installed': installed
            }
