# GDG Leaderboard Project

This repository contains the backend API and frontend application for the Google Cloud Study Jams 2025 Leaderboard, designed to track participant progress based on daily CSV reports.

## Project Structure (Monorepo)

This project uses a monorepo structure, containing two main sub-directories:

-   `GDG_Leaderboard_Backend/`: Contains the Python FastAPI application, database scripts, and CSV import logic. This is where the leaderboard data is processed and served via an API.
-   `GDG_Leaderboard_Frontend/`: (To be populated by the frontend team) This will contain the Next.js/React application responsible for displaying the leaderboard and other program statistics.

## Getting Started

Follow these steps to set up and run the backend, and to prepare your local environment for frontend development.

### 1. Initial Setup (One-Time)

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/GDG_Leaderboard.git
    cd GDG_Leaderboard
    ```
2.  **Backend Setup (`GDG_Leaderboard_Backend`):**
    *   Navigate into the backend directory:
        ```bash
        cd GDG_Leaderboard_Backend
        ```
    *   **Create Python Virtual Environment:**
        ```bash
        python -m venv venv
        ```
    *   **Activate Virtual Environment:**
        *   Windows: `.\venv\Scripts\activate`
        *   macOS/Linux: `source venv/bin/activate`
    *   **Install Python Dependencies:**
        ```bash
        pip install -r requirements.txt # (Initially, this will be the packages from our setup: fastapi uvicorn mysql-connector-python python-dotenv pytz)
        ```
    *   **Create `.env` file:** In the `GDG_Leaderboard_Backend/` directory, create a file named `.env`.
        *   **Securely obtain the MySQL and FastAPI credentials** (e.g., via a secure message or verbally) and paste them into your `.env` file. It should look like this:
            ```
            # MySQL Database Configuration
            DATABASE_HOST="127.0.0.1"
            DATABASE_PORT="3306"
            DATABASE_USER="your_mysql_user"
            DATABASE_PASSWORD="your_mysql_password"
            DATABASE_NAME="gdglink_db"

            # FastAPI Server Configuration
            FASTAPI_PORT="8000"
            CORS_ORIGINS="*" # For local development. For production, specify frontend URL(s).
            ```
    *   **Set up MySQL Database:**
        *   Ensure you have a local MySQL server running (e.g., via MySQL Workbench).
        *   **Crucially, drop any existing `users` or `badges` tables** in your `gdglink_db` (or whatever `DATABASE_NAME` you're using) to ensure a clean schema creation.
        *   **Create the database tables:** Run the API once (this will call `database.py` to create tables):
            ```bash
            python api_main.py
            ```
            *You should see "✅ Database tables ensured to exist (users table only)" in the console.*
        *   Press `CTRL + C` to stop the API after table creation.
        *   *(Optional: Verify in MySQL Workbench that the `users` table exists with columns: `id`, `name`, `email`, `skillsboost_url`, `verified`, `total_skill_badges`, `total_arcade_games`, `all_access_completed`).*

### 2. Daily Data Update & Running the Backend

This is the routine you will follow each time you receive a new CSV report.

1.  **Stop the Backend API:** If `api_main.py` is currently running, go to its terminal window and press `CTRL + C`.
2.  **Place New CSV:** Copy your new daily CSV file into the `GDG_Leaderboard_Backend/` directory.
3.  **Update `import_csv_data.py`:**
    *   Open `GDG_Leaderboard_Backend/import_csv_data.py`.
    *   **Change the `csv_file_path` variable** to point to your new CSV file.
        ```python
        # Example for Windows:
        csv_file_path = "C:\\Users\\YOUR_USER\\OneDrive\\Desktop\\GDG_Leaderboard\\GDG_Leaderboard_Backend\\MGM's Jawaharlal Nehru Engineering College - Aurangabad, India [DATE].csv"
        ```
    *   Save the file.
4.  **Run the Import Script:**
    *   Ensure your Python virtual environment is active (from step 1).
    *   Execute the import script:
        ```bash
        python import_csv_data.py
        ```
    *   *You should see "Processed (Row X): ..." messages for each user, indicating successful data import.*
5.  **Start the Backend API:**
    *   Once the import script finishes, start the FastAPI application:
        ```bash
        python api_main.py
        ```
    *   *Leave this terminal window running while the frontend (or API access) is needed.*

### 3. Frontend Development (`GDG_Leaderboard_Frontend`)

*(This section is for your frontend team)*

1.  **Navigate into the frontend directory:**
    ```bash
    cd GDG_Leaderboard_Frontend
    ```
2.  **Initialize & Install Dependencies:**
    *   If starting from scratch, initialize a Next.js project here or clone an existing one.
    *   Install Node.js dependencies: `npm install` (or `yarn install`).
3.  **Configure API Base URL:**
    *   Create a `.env.local` file in the `GDG_Leaderboard_Frontend/` directory.
    *   Add the backend API's local URL:
        ```
        NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/
        ```
4.  **Update API Endpoints:**
    *   **Crucially, update all API fetch requests in the frontend code** to use the custom endpoints provided by the backend.
    *   Search for `/api/leaderboard`, `/api/all_progress`, `/api/stats` and **replace them with:**
        *   `/custom/leaderboard`
        *   `/custom/all_progress`
        *   `/custom/stats`
5.  **Adapt Data Display:**
    *   The backend's API now provides specific fields: `Rank`, `Student Name`, `Code Redemption Status`, `All Badges and Skills Completed`, `Number of Skill Badges Completed`, `Arcade Game Completion`.
    *   Modify frontend components to display *only* these fields, removing any old logic for individual badges if present.
6.  **Run Frontend Locally:**
    *   Ensure the backend API (`api_main.py`) is running in a separate terminal.
    *   In the frontend directory: `npm run dev` (or `yarn dev`).
    *   Access the frontend in your browser (usually `http://localhost:3000`).

## Backend API Endpoints

Once `api_main.py` is running, the following endpoints are available:

-   **Root:** `http://127.0.0.1:8000/`
-   **API Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`
-   **API Documentation (ReDoc):** `http://127.0.0.1:8000/redoc`
-   **Top 10 Leaderboard:** `http://127.0.0.1:8000/custom/leaderboard`
-   **All Users Progress:** `http://127.0.0.1:8000/custom/all_progress`
-   **Overall Statistics:** `http://127.0.0.1:8000/custom/stats`

## Troubleshooting

-   **`Database connection failed`:** Check your `.env` file for correct `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`. Ensure your MySQL server is running.
-   **`Unknown column ...` or `SQL syntax error`:** This indicates a mismatch between your `database.py` schema definition and what's actually in your MySQL database. **Always drop both `users` and `badges` tables in MySQL Workbench, then run `python api_main.py` once to recreate them, before running `import_csv_data.py`.**
-   **Frontend `Network Error` or `404 Not Found`:** Ensure your backend API (`api_main.py`) is running. Verify the `NEXT_PUBLIC_API_BASE_URL` in your frontend's `.env.local` file is correct, and that frontend API calls use the correct paths (`/custom/leaderboard`, etc.).
-   **Empty Leaderboard on Frontend/API:**
    1.  Confirm `api_main.py` is running.
    2.  Check `http://127.0.0.1:8000/custom/leaderboard` in your browser directly. If it's empty, `import_csv_data.py` either failed or didn't run, or `verified = 1` condition in the queries is not met by any user.
    3.  Inspect the `users` table in MySQL Workbench (`SELECT * FROM users;`) to ensure data is present and columns like `total_skill_badges` and `verified` have expected values (e.g., `1` for verified, actual badge numbers).

---
