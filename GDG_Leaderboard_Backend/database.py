import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Optional
import logging
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

print("--- DEBUG: database.py version 3.0 loaded at", datetime.now(), "---") # TOP-LEVEL DEBUG PRINT

KOLKATA_TZ = pytz.timezone('Asia/Kolkata')

def get_kolkata_time():
    return datetime.now(KOLKATA_TZ)

# Database Configuration from .env
DB_CONFIG = {
    'host': os.getenv("DATABASE_HOST"),
    'port': int(os.getenv("DATABASE_PORT")),
    'user': os.getenv("DATABASE_USER"),
    'password': os.getenv("DATABASE_PASSWORD"),
    'database': os.getenv("DATABASE_NAME"),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True,
    'time_zone': '+05:30'
}

logger = logging.getLogger('database')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Define total expected badges for display purposes in API
TOTAL_EXPECTED_BADGES_FOR_PROGRAM = 20 # Assuming your program has 20 total badges/games

class DatabaseOperations:
    def __init__(self):
        self.connection = None
        self.connect()
        self.ensure_tables_exist()

    def connect(self) -> bool:
        try:
            if self.connection and self.connection.is_connected():
                return True
            self.connection = mysql.connector.connect(**DB_CONFIG)
            logger.info("✅ Successfully connected to MySQL database")
            return True
        except Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def ensure_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def ensure_tables_exist(self):
        self.ensure_connection()
        cursor = self.connection.cursor()
        try:
            # Users table: Directly stores CSV data, including badge counts and completion status
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    skillsboost_url VARCHAR(500) NOT NULL UNIQUE,
                    verified BOOLEAN DEFAULT FALSE, /* Mapped to "Code Redemption Status" */
                    total_skill_badges INT DEFAULT 0, /* Mapped to "Number of Skill Badges Completed" */
                    total_arcade_games INT DEFAULT 0, /* Mapped to "Arcade Game Completion" */
                    all_access_completed BOOLEAN DEFAULT FALSE, /* Mapped to "All Badges and Skills Completed" */
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_email (email),
                    INDEX idx_skillsboost_url (skillsboost_url),
                    INDEX idx_verified (verified)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            self.connection.commit()
            logger.info("✅ Database tables ensured to exist (users table only)")
        except Error as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
        finally:
            cursor.close()

    def get_all_user_progress(self) -> Dict:
        """Get progress data for all verified users directly from the users table, formatted for specific columns."""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        try:
            sql_query_all_progress = """
                SELECT
                    u.id,
                    u.name,
                    u.verified,
                    u.total_skill_badges,
                    u.total_arcade_games,
                    u.all_access_completed,
                    u.updated_at AS latest_updated_date
                FROM users u
                WHERE u.verified = 1
                ORDER BY (u.total_skill_badges + u.total_arcade_games) DESC, u.updated_at ASC, u.name ASC /* CHANGED: used u.updated_at */
            """
            print("\n--- DEBUG: get_all_user_progress SQL ---") # DEBUG PRINT
            print(sql_query_all_progress) # DEBUG PRINT
            cursor.execute(sql_query_all_progress)
            users_data = cursor.fetchall()

            users_list = []
            rank = 1

            for user in users_data:
                users_list.append({
                    "Rank": rank,
                    "Student Name": user['name'],
                    "Code Redemption Status": "Redeemed" if user['verified'] else "Not Redeemed",
                    "All Badges and Skills Completed": "Yes" if user['all_access_completed'] else "No",
                    "Number of Skill Badges Completed": user['total_skill_badges'],
                    "Arcade Game Completion": user['total_arcade_games'],
                })
                rank += 1
            
            return {
                "program_name": "Google Cloud Study Jams 2025",
                "total_users": len(users_list),
                "users": users_list
            }

        except Exception as e:
            logger.error(f"Error getting all user progress: {e}")
            return {
                "program_name": "Google Cloud Study Jams 2025",
                "total_users": 0,
                "users": []
            }
        finally:
            cursor.close()

    def get_leaderboard(self) -> Dict:
        """Get leaderboard data - top performers, directly from users table, formatted for specific columns."""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)

        try:
            sql_query_leaderboard = """
                SELECT
                    u.id,
                    u.name,
                    u.verified,
                    u.total_skill_badges,
                    u.total_arcade_games,
                    u.all_access_completed,
                    u.updated_at AS latest_updated_date
                FROM users u
                WHERE u.verified = 1
                ORDER BY (u.total_skill_badges + u.total_arcade_games) DESC, u.updated_at ASC, u.name ASC /* CHANGED: used u.updated_at */
                LIMIT 10
            """
            print("\n--- DEBUG: get_leaderboard SQL (Top Performers) ---") # DEBUG PRINT
            print(sql_query_leaderboard) # DEBUG PRINT
            cursor.execute(sql_query_leaderboard)
            users_data = cursor.fetchall()

            # Get total participants count
            sql_count_query = "SELECT COUNT(*) as total FROM users WHERE verified = 1"
            print("\n--- DEBUG: get_leaderboard SQL (Total Participants Count) ---") # DEBUG PRINT
            print(sql_count_query) # DEBUG PRINT
            cursor.execute(sql_count_query)
            total_participants = cursor.fetchone()['total']

            top_performers = []
            rank = 1

            for user in users_data:
                top_performers.append({
                    "Rank": rank,
                    "Student Name": user['name'],
                    "Code Redemption Status": "Redeemed" if user['verified'] else "Not Redeemed",
                    "All Badges and Skills Completed": "Yes" if user['all_access_completed'] else "No",
                    "Number of Skill Badges Completed": user['total_skill_badges'],
                    "Arcade Game Completion": user['total_arcade_games'],
                })
                rank += 1

            return {
                "program_name": "Google Cloud Study Jams 2025",
                "top_performers": top_performers,
                "total_participants": total_participants,
                "last_updated": get_kolkata_time().isoformat(),
                "mode": "csv-driven"
            }

        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return {
                "program_name": "Google Cloud Study Jams 2025",
                "top_performers": [],
                "total_participants": 0,
                "last_updated": get_kolkata_time().isoformat(),
                "mode": "csv-driven"
            }
        finally:
            cursor.close()
            
    def get_stats(self) -> Dict:
        """Get overall statistics, updated for CSV direct counts."""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        try:
            sql_stats_query = """
                SELECT
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN verified = 1 THEN 1 END) as verified_users,
                    COUNT(CASE WHEN all_access_completed = TRUE THEN 1 END) as completed_users,
                    COALESCE(SUM(total_skill_badges), 0) + COALESCE(SUM(total_arcade_games), 0) as total_badges_earned,
                    COUNT(CASE WHEN (total_skill_badges + total_arcade_games) > 0 THEN 1 END) as users_with_badges
                FROM users
                WHERE verified = 1
            """
            print("\n--- DEBUG: get_stats SQL (Main Stats) ---") # DEBUG PRINT
            print(sql_stats_query) # DEBUG PRINT
            cursor.execute(sql_stats_query)
            stats_data = cursor.fetchone()

            total_users = stats_data['total_users'] or 0
            verified_users = stats_data['verified_users'] or 0
            completed_users = stats_data['completed_users'] or 0
            total_badges_earned = stats_data['total_badges_earned'] or 0
            users_with_badges = stats_data['users_with_badges'] or 0

            average_badges = int(total_badges_earned / max(users_with_badges, 1))

            sql_top_performer_query = """
                SELECT name, skillsboost_url, (total_skill_badges + total_arcade_games) AS combined_badges
                FROM users
                WHERE verified = 1
                ORDER BY combined_badges DESC, updated_at ASC, name ASC
                LIMIT 1
            """
            print("\n--- DEBUG: get_stats SQL (Top Performer) ---") # DEBUG PRINT
            print(sql_top_performer_query) # DEBUG PRINT
            cursor.execute(sql_top_performer_query)
            top_user = cursor.fetchone()

            top_performer = {}
            if top_user:
                top_performer = {
                    "name": top_user['name'],
                    "badge_count": top_user['combined_badges'],
                    "profile_url": top_user['skillsboost_url']
                }
            
            sql_distribution_query = """
                SELECT (total_skill_badges + total_arcade_games) as badge_sum, COUNT(*) as user_count
                FROM users WHERE verified = 1
                GROUP BY badge_sum ORDER BY badge_sum ASC
            """
            print("\n--- DEBUG: get_stats SQL (Completion Distribution) ---") # DEBUG PRINT
            print(sql_distribution_query) # DEBUG PRINT
            cursor.execute(sql_distribution_query)
            dist_results = cursor.fetchall()
            for row in dist_results:
                completion_distribution[str(row['badge_sum'])] = row['user_count']
            
            progress_timeline = {} # Not feasible without individual badge dates

            completion_percentage = 0
            tier_name = "Tier 3"
            tier_emoji = "🥉"
            tier_target = 50

            if completed_users >= 1:
                 completion_percentage = min(int((completed_users / 50) * 100), 100)
                 if completion_percentage >= 70:
                    tier_name = "Tier 1"
                    tier_emoji = "🥇"
                    tier_target = 100
                 elif completion_percentage >= 50:
                    tier_name = "Tier 2"
                    tier_emoji = "🥈"
                    tier_target = 70
                 else:
                    tier_name = "Tier 3"
                    tier_emoji = "🥉"
                    tier_target = 50

            return {
                "program_name": "Google Cloud Study Jams 2025",
                "total_users": total_users,
                "verified_users": verified_users,
                "completed_users": completed_users,
                "total_badges": TOTAL_EXPECTED_BADGES_FOR_PROGRAM,
                "total_badges_earned": total_badges_earned,
                "completion_percentage": completion_percentage,
                "tier": tier_name,
                "tier_emoji": tier_emoji,
                "tier_target": tier_target,
                "average_badges": average_badges,
                "badge_completion_stats": {},
                "completion_distribution": completion_distribution,
                "top_performer": top_performer,
                "progress_timeline": progress_timeline,
                "last_updated": get_kolkata_time().isoformat(),
                "mode": "csv-driven"
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "program_name": "Google Cloud Study Jams 2025",
                "total_users": 0, "verified_users": 0, "completed_users": 0, "total_badges": TOTAL_EXPECTED_BADGES_FOR_PROGRAM,
                "completion_percentage": 0, "tier": "Tier 3", "tier_emoji": "🥉",
                "tier_target": 50, "average_badges": 0,
                "badge_completion_stats": {}, "completion_distribution": {},
                "top_performer": {}, "progress_timeline": {},
                "last_updated": get_kolkata_time().isoformat(), "mode": "csv-driven"
            }
        finally:
            cursor.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("📝 Database connection closed")

db = DatabaseOperations()

if __name__ == "__main__":
    print("🧪 Testing database connection...")
    if db.connection and db.connection.is_connected():
        print("✅ Database connection test passed")
        try:
            cursor = db.connection.cursor(dictionary=True) # Use dictionary=True for easier access to results
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE verified = 1")
            result = cursor.fetchone()
            print(f"✅ Database query test passed: {result['total']} verified users")
            cursor.close()
        except Exception as e:
            print(f"❌ Database query test failed: {e}")
    print("🎉 Database module loaded successfully!")