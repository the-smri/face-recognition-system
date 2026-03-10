# Face Recognition Attendance System

A complete web-based face recognition attendance application built with Python (Flask) and OpenCV.

## Features

- **Admin Dashboard**: Real-time stats of registered users and daily attendance.
- **User Registration**: Register students/employees using the webcam with automatic multi-frame face encoding.
- **Real-Time Recognition**: Live camera feed to match faces and automatically log attendance.
- **History & Logging**: Searchable and filterable table of attendance records.
- **CSV Export**: Instantly export the attendance database to Excel/CSV.

## Tech Stack

- Frontend: HTML5, JavaScript (ES6), Bootstrap 5, FontAwesome
- Backend: Python 3, Flask
- Computer Vision: OpenCV, `face_recognition` (dlib)
- Database: SQLite, Pandas

## Setup Instructions

1. **Activate Virtual Environment** (Required)
   Ensure you are using the provided virtual environment where dependencies are already installed.

   ```powershell
   # Windows
   .\venv\Scripts\activate
   ```

2. **Run the Application**

   ```powershell
   python app.py
   ```

   The database and required folders will automatically be initialized on the first run.

3. **Access the Web Dashboard**
   Open your browser and navigate to [http://localhost:5000](http://localhost:5000)

4. **Login**
   - Username: `admin`
   - Password: `admin`

## Folder Structure

- `/dataset` - Stores captured face images during registration
- `/encodings` - Stores the pickled encodings dataset for recognition
- `/database` - SQLite DB file (`attendance.db`)
- `/attendance` - Stores exported CSV files
- `/templates` - HTML views
- `/static` - CSS and JavaScript assets

_Note: Ensure you have a working webcam connected, and provide permission in your browser when requested._
