# Tech Stack Setup for Spotify Downloader

This document provides instructions for setting up the tech stack used in the Spotify Downloader project.

## Tech Stack
- **Backend:** Python (Flask)
- **Frontend:** React (Vite with Tailwind CSS)

## Cloning and Setting Up the Repository

To clone and set up the repository using Docker, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/spotify-downloader.git
   cd spotify-downloader
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t spotify-downloader:latest .
   ```

3. **Run the Docker container:**
   ```bash
   docker run -p 5000:5000 -p 3000:3000 spotify-downloader:latest
   ```

## Local Setup for Flask Backend

To set up the Flask backend locally using a virtual environment, follow these steps:

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Create a `.env` file in the root directory and add the following variables:
   ```env
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
   FRONTEND_URL=http://localhost:3000
   ```

5. **Run the Flask application:**
   ```bash
   python backend/app.py
   ```

## Setting Up the React Frontend

To set up the React frontend using Vite and Tailwind CSS, follow these steps:

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Initialize a new Vite project:**
   ```bash
   npm create vite@latest
   ```

3. **Install Tailwind CSS:**
   Follow the official Tailwind CSS installation guide for Vite:
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

4. **Configure Tailwind CSS:**
   Update the `tailwind.config.js` file:
   ```javascript
   module.exports = {
     content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
     theme: {
       extend: {},
     },
     plugins: [],
   };
   ```

5. **Add Tailwind directives to your CSS:**
   In your main CSS file (e.g., `src/index.css`), add the following:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

6. **Run the React application:**
   ```bash
   npm install
   npm run dev
   ```

## Additional Notes

Make sure you have Docker installed on your machine before running the above commands. For any issues, please refer to the project's main README or open an issue in the repository.
