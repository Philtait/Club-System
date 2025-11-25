# 📚 Club Management System for Strathmore University

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-orange?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![PayPal](https://img.shields.io/badge/PayPal-blue?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/)
[![Nginx](https://img.shields.io/badge/Nginx-green?style=for-the-badge&logo=nginx&logoColor=white)](https://www.nginx.com/)

A web-based Club Management System developed as a third-year Computer Science project at **Strathmore University**. This platform simplifies the management of student clubs, event planning, member engagement, and administrative oversight through a centralized, role-based portal.

**The application is fully deployed and live at: [https://philtait.me](https://philtait.me)**

---

## Table of Contents
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [Technology Stack](#technology-stack)
- [Deployment & Server Administration](#deployment--server-administration)
- [Getting Started Locally](#getting-started-locally)
- [Authors](#authors)
- [Acknowledgments](#acknowledgments)

---

## Problem Statement

The management of student clubs at Strathmore University traditionally relied on manual, fragmented methods like WhatsApp, posters, and Google Forms. This led to inconsistent communication, a heavy administrative workload, and a lack of data for tracking student engagement. This project aims to solve these challenges by providing a unified and efficient digital solution.

## Key Features

-   🔒 **Role-Based Access Control:** Differentiated dashboards and permissions for **Students**, **Club Leaders**, and **Administrators**.
-   📝 **Club Approval Workflow:** A formal system for students to request new clubs and for administrators to review and approve them.
-   📆 **Event Management:** Club leaders can schedule events, which students can then browse and register for.
-   👥 **Membership Management:** Students can submit requests to join clubs, and leaders can manage their member lists from a dedicated dashboard.
-   📢 **Real-Time Notifications:** An in-app notification system and email alerts for key actions (e.g., new event, membership approval).
-   💬 **Feedback System:** A mechanism for students to submit feedback and ratings on club events.
-   💳 **Payment Integration:** Securely handle membership fees or event tickets using the **PayPal** API.

---

## Screenshots

*(Homepage of the deployed application)*
![Homepage Screenshot](https://github.com/user-attachments/assets/875d952b-3dad-4774-9536-a59df25a8e7c)
---

## Technology Stack

| Category              | Technology                                       |
| --------------------- | ------------------------------------------------ |
| **Backend**           | Python, Flask, SQLAlchemy                        |
| **Frontend**          | HTML, CSS, JavaScript, Jinja2                    |
| **Database**          | MySQL                                            |
| **Payment Gateway**   | PayPal                                           |
| **Version Control**   | Git, GitHub                                      |
| **Design & Diagrams** | Figma, Draw.io                                   |

---

## Deployment & Server Administration

The application is deployed on a cloud server, configured and managed with the following production stack:

-   **Cloud Provider**: Microsoft Azure Virtual Machine
-   **Operating System**: Ubuntu Server
-   **Web Server**: Nginx (configured as a Reverse Proxy)
-   **WSGI Server**: Gunicorn (running as a daemon process)
-   **Security**:
    -   SSL/TLS certificate from Let's Encrypt (Certbot) for HTTPS encryption.
    -   UFW (Uncomplicated Firewall) configured to secure network ports.
    -   Scrypt hashing for secure password storage.
-   **Monitoring**: Proactive alerting system via a custom bash script and Cron job, using SendGrid as an SMTP relay for email notifications on service failures.

---

## Getting Started Locally

To get a local copy up and running for development purposes, follow these steps.

### Prerequisites

-   Python 3.8+
-   MySQL Server
-   Git

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Philtait/Club-System.git
    cd Club-System
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv env
    source env/bin/activate

    # For Windows
    python -m venv env
    .\env\Scripts\activate
    ```

3.  **Install project dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**
    -   Log in to your MySQL server.
    -   Create a new database for the project: `CREATE DATABASE clubs;`

5.  **Configure environment variables:**
    -   Create a new file named `.env` in the project's root directory.
    -   Add the following variables, replacing the values with your own credentials. **This file should be included in your `.gitignore` and never committed.**
        ```ini
        SECRET_KEY='your-very-secure-random-secret-key-here'
        DATABASE_URL='mysql+pymysql://<db_user>:<db_password>@<db_host>/clubs'
        PAYPAL_CLIENT_ID='your_paypal_client_id'
        PAYPAL_CLIENT_SECRET='your_paypal_client_secret'
        ```

6.  **Run the Flask development server:**
    ```bash
    flask run
    ```
    The application will now be running at `http://127.0.0.1:5000`.

---

## Authors

-   **Tait Philip Lemaron** - [Philtait](https://github.com/Philtait)
-   **Morara Daniel Momanyi**

## Acknowledgments

-   We would like to express our sincere gratitude to our supervisor, **Dr. Kennedy Ronoh**, for his continuous support and guidance throughout this project.
