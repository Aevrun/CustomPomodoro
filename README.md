# 🍅 Custom Pomodoro + Time Tracker

### Tired of subscriptions? Build your own focus with advanced tracking!

This project is a robust, customizable **Pomodoro Timer and Time Tracker** application built using **Streamlit** and **Python**. It goes beyond a standard timer by allowing users to **log sessions, assign categories, manually add entries, and view summary analytics**, providing a powerful, subscription-free, and fully controlled productivity tool.

---

## ✨ Key Features

* **Integrated Time Tracker:** Automatically saves all completed Pomodoro sessions (including minutes worked, start/end times, and subject) to a local `pomodoro_data.csv` file.
* **Customization:** Easily set custom **Work** and **Break** durations.
* **Session Management:** Features **Pause, Resume, Stop & Save, and Cancel** functionality.
* **Category System:** Manage a list of subjects/categories via a local `categories.txt` file and assign them to sessions for better tracking.
* **Data Analysis:** Includes built-in dashboards for:
    * Today's sessions.
    * Daily totals over the last 7 days.
    * Weekly totals broken down by Category.
    * All-time totals by Category.
* **Data Editing:** Use a Streamlit **data editor** to modify or delete past entries directly within the app.
* **Manual Entry Form:** Easily log time retroactively.
* **Sound Alert:** Plays a sound (`alarm.mp3`) when a session is complete (optional file).

---

## 💻 Technology Stack

* **Python:** The core programming language.
* **Streamlit:** Used for creating the interactive web application and data dashboard interface.
* **Pandas:** Used for efficient data storage, retrieval, and analysis (CSV file handling).

---

## 🚀 Getting Started

These instructions will get a copy of the project up and running on your local machine.

### Prerequisites

You will need **Python (3.7+)** and **pip** installed on your system.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/Custom-Pomodoro.git](https://github.com/YourUsername/Custom-Pomodoro.git)
    cd Custom-Pomodoro
    ```
2.  **Create a virtual environment** (Recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the required dependencies:**
    *(The script uses `streamlit` and `pandas`)*
    ```bash
    pip install streamlit pandas
    ```
4.  **Optional: Add Alarm Sound:**
    * For the sound feature to work, place an MP3 file named **`alarm.mp3`** in the root directory of the project. If the file is missing, the app will display a notification instead.

### Running the Application Locally

1.  Make sure you are in the root directory of the project.
2.  Run the Streamlit application using the main file name:
    ```bash
    streamlit run pomodoro.py
    ```
3.  Your browser should automatically open to the application (usually at `http://localhost:8501`).

---

## ☁️ File Structure & Data

The application manages two primary files for persistent data:

| File Name | Purpose | Format |
| :--- | :--- | :--- |
| `pomodoro_data.csv` | Stores all completed and manually added work sessions, including minutes, subject, and category. | CSV (Comma Separated Values) |
| `categories.txt` | Stores a simple list of user-defined categories for subject organization. | Plain Text (one category per line) |

---

## 🤝 Contribution

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Implement Amazing Feature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---
