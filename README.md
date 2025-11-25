# 📚 Club Management System

A web-based Club Management System developed as a third-year Computer Science project at **Strathmore University**.

This platform simplifies the management of student clubs, event planning, member engagement, feedback collection, and administrative oversight through a centralized portal.

---

## 🚀 Features

- 🔒 Role-based access for **Students**, **Club Leaders**, and **Administrators**
- 📝 Club creation request and approval workflow
- 📆 Event scheduling, announcement, and registration
- 👥 Membership management (join/exit clubs)
- 📢 Real-time notifications and email alerts
- 💬 Feedback submission and review
- 📊 Admin dashboards for club and event monitoring
- 💳 **M-PESA** integration for membership payments

---

## 🧰 Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript, Jinja2
- **Database**: MySQL
- **Tools**: Figma, Postman, Git, Draw.io

---

## 🛠️ Getting Started

### ✅ Prerequisites

- Python 3.10+
- MySQL Server
- pip (Python package manager)
- Git

---

### ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Club-Management-System.git

# Navigate to the project directory
cd Club-Management-System

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install project dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Open the .env file and set your DB credentials and secret key

# Run the Flask development server
flask run
