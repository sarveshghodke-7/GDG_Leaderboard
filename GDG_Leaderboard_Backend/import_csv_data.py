import csv
import os
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def import_csv_to_mysql(csv_filepath):
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DATABASE_HOST"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            database=os.getenv("DATABASE_NAME"),
            port=int(os.getenv("DATABASE_PORT"))
        )
        cursor = connection.cursor()

        # --- DATABASE TABLE AND COLUMN NAMES ---
        # Assumes the 'users' table has these columns, matching the new database.py:
        # id, name, email, skillsboost_url, verified,
        # total_skill_badges, total_arcade_games, all_access_completed,
        # created_at, updated_at

        users_table_name = "users"

        # SQL to insert new user data or update existing user data in the 'users' table
        insert_update_user_sql = f"""
        INSERT INTO {users_table_name} (
            name, email, skillsboost_url, verified,
            total_skill_badges, total_arcade_games, all_access_completed, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            email = VALUES(email),
            skillsboost_url = VALUES(skillsboost_url),
            verified = VALUES(verified),
            total_skill_badges = VALUES(total_skill_badges),
            total_arcade_games = VALUES(total_arcade_games),
            all_access_completed = VALUES(all_access_completed),
            updated_at = VALUES(updated_at)
        """

        with open(csv_filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            print(f"Starting CSV data import from: {csv_filepath}")
            for i, row in enumerate(reader):
                user_name_csv = row.get('User Name', '').strip()
                user_email = row.get('User Email', '').strip()
                skillsboost_url = row.get('Google Cloud Skills Boost Profile URL', '').strip()
                
                profile_url_status = row.get('Profile URL Status', '').strip().lower()
                access_code_status = row.get('Access Code Redemption Status', '').strip().lower()
                
                # Determine 'verified' status based on CSV data
                is_verified = (profile_url_status == 'all good' and access_code_status == 'yes')
                
                # Get badge and game counts directly from CSV
                try:
                    total_skill_badges = int(row.get('# of Skill Badges Completed', 0))
                except ValueError:
                    total_skill_badges = 0
                
                try:
                    total_arcade_games = int(row.get('# of Arcade Games Completed', 0))
                except ValueError:
                    total_arcade_games = 0
                
                # Determine 'all_access_completed' status from CSV
                all_access_completed_status = (row.get('All Skill Badges & Games Completed', 'No').strip().lower() == 'yes')
                
                current_timestamp = datetime.now()

                # Basic validation: Skip row if essential data is missing
                if not user_name_csv or not user_email or not skillsboost_url:
                    print(f"Skipping row {i+2} (CSV line {i+2}) due to missing name, email or profile URL.")
                    continue

                try:
                    cursor.execute(insert_update_user_sql, (
                        user_name_csv,
                        user_email,
                        skillsboost_url,
                        is_verified,
                        total_skill_badges,
                        total_arcade_games,
                        all_access_completed_status,
                        current_timestamp
                    ))
                    print(f"Processed (Row {i+2}): {user_name_csv} ({user_email}) - Skill Badges: {total_skill_badges}, Arcade Games: {total_arcade_games}, All Access: {all_access_completed_status}")

                except mysql.connector.Error as err:
                    print(f"Error processing {user_name_csv} ({user_email}) on row {i+2}: {err}")
                    connection.rollback()
            
        connection.commit()
        print("\nCSV data import complete!")

    except mysql.connector.Error as err:
        print(f"Database connection or operation error: {err}")
    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_filepath}'. Please check the path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    # --- IMPORTANT: CHANGE THIS TO THE ACTUAL PATH OF YOUR DAILY CSV FILE ---
    # Example: r"C:\Users\YourUser\Documents\your_file.csv"
    
    # Placeholder path for your provided CSV format:
    csv_file_path = "C:\\Users\\Asus\\OneDrive\\Desktop\\GDG_Leaderboard\\GDG_Leaderboard_Backend\\MGM's Jawaharlal Nehru Engineering College - Aurangabad, India [17 Oct].csv"
    
    import_csv_to_mysql(csv_file_path)