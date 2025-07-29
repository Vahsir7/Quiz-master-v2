# QuizMaster v2 🎯

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

QuizMaster v2 is a full-featured, interactive quiz platform designed for educational environments. It provides a seamless experience for both administrators and students, featuring a robust backend powered by Flask and a dynamic, responsive frontend built with Vue.js.

## Key Features

### For Administrators
- **Dashboard Analytics**: Visualize key metrics like total students, exam attempts, and average scores per subject
- **Content Management**: Full CRUD (Create, Read, Update, Delete) functionality for Subjects, Chapters, Exams, and Questions
- **Student Management**: View registered students, check their details, and manage accounts
- **Exam Publishing**: Control exam visibility and automatically notify students when new exams are published
- **Automated Reporting**: Trigger asynchronous tasks to generate and email performance reports to students

### For Students
- **Personalized Dashboard**: Track performance with stats on quizzes taken, overall average score, and performance trends
- **Exam Portal**: Browse and take available exams, filtered by subject or chapter
- **Interactive Quiz Interface**: Clean, timed interface for taking quizzes with real-time progress tracking
- **Instant Results**: View detailed results immediately after submitting an exam, including correct answers and your selections
- **Quiz History**: Review all past attempts and export quiz history to CSV format

## 🛠️ Tech Stack

| **Area** | **Technology** |
|----------|----------------|
| **Backend** | Flask, SQLAlchemy, Celery, Redis, PyJWT |
| **Frontend** | Vue.js, Pinia, Vue Router, Axios, Chart.js |
| **Database** | SQLite (default) |
| **Message Broker** | Redis |
| **Task Queue** | Celery |

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python** (3.8 or higher)
- **Node.js** (14.x or higher) and npm
- **Redis Server** (for Celery message broker and caching)

## 🚀 Installation and Setup

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/Vahsir7/Quiz-master-v2.git
cd quiz-master-v2
```

### 2. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
# Navigate to the backend folder
cd backend

# Create and activate a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
```

> **Note**: The project includes a default `.env` file with pre-configured settings.

### 3. Frontend Setup

Open a new terminal, navigate to the frontend directory, and install the necessary npm packages:

```bash
# Navigate to the frontend folder
cd frontend

# Install npm dependencies
npm install
```

## 🏃‍♂️ Running the Application

To run the application, you need to start the Redis server, the backend (Flask), the frontend (Vue), and the Celery worker. Each service should be run in a separate terminal window.

### Terminal 1: Start Redis

Make sure your Redis server is running. If not, start it using the command appropriate for your system:

```bash
redis-server
```

### Terminal 2: Start the Celery Worker

The Celery worker handles background tasks like sending emails:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
celery -A celery_worker.celery worker --loglevel=info
```

### Terminal 3: Start the Celery Beat Scheduler

The Celery Beat scheduler is responsible for periodic tasks, like sending daily reminders:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
celery -A celery_worker.celery beat --loglevel=info
```

### Terminal 4: Start the Flask Backend Server

This will run the main API server:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
flask run
```

The backend will be available at <http://127.0.0.1:5000>.

### Terminal 5: Start the Vue.js Frontend

This will launch the user interface:

```bash
cd frontend
npm run dev
```

The frontend will be available at the URL provided by the npm run dev command (usually <http://localhost:5173>).

You can register new student accounts directly through the application's registration page.

## 📁 Project Structure

```text
Quiz-master-v2/
├── backend/                 # Flask backend
│   ├── app/
│   │   ├── controllers/     # API route handlers
│   │   ├── models.py        # Database models
│   │   ├── config.py        # Configuration settings
│   │   └── __init__.py      # App factory
│   ├── requirements.txt     # Python dependencies
│   └── celery_worker.py     # Celery worker setup
├── frontend/                # Vue.js frontend
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/          # Page components
│   │   ├── router/         # Vue Router setup
│   │   └── stores/         # Pinia stores
│   └── package.json        # Node.js dependencies
└── README.md               # Project documentation
```

Made with ❤️ for educational purposes