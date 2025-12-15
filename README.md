🎫 Role-Based Ticket Management System

A scalable and intelligent Ticket Management System built with Django REST Framework and React to manage customer support tickets efficiently. Supports three roles—User, Agent, and Admin—with JWT-based authentication and role-based authorization.
______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________
✨ Features

📝 Ticket Management: Create, view, update, and delete tickets via REST APIs.

👥 Role-Based Access: Secure access for Users, Agents, and Admins.

🤖 AI/ML Priority Detection: Automatically assigns ticket priority based on keywords.

📧 Email Notifications: Automatic acknowledgment and updates via Celery.

🔄 Background Task Assignment: Tickets assigned to agents based on workload and priority.
______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________


🖥️ Dashboards

👤 User Dashboard: Track submitted tickets, status, and attachments.

🛠️ Agent Dashboard: View assigned tickets, SLA alerts, and update statuses.

📊 Admin Dashboard: Manage tickets, agents, categories, and view analytics reports.

⏱️ SLA Reports: Daily reports in PDF/CSV with SLA breach analysis.
______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________



🛠️ Tech Stack

Backend: Python, Django, Django REST Framework

Frontend: React, Redux

Database: PostgreSQL

Async Tasks: Celery, Redis

Authentication: JWT (Simple JWT)

AI/ML Module: Python (Scikit-learn / NLP)

Email: SMTP via Celery
______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________


🚀 Future Scope

⚡ Real-Time Notifications: WebSocket/Django Channels for instant updates.

🧠 Advanced AI/ML: Predictive SLA estimation, smart ticket routing, sentiment analysis.

📱 Mobile Support: React Native / Flutter apps for users and agents.

🔗 Integration: Slack, Teams, CRM systems for unified ticketing.

______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

🏁 Getting Started
Clone the Repository
git clone https://github.com/ashwiniwakhare/CapstoneBackend

Backend Setup:

->>pip install -r requirements.txt

->>python manage.py migrate

->>python manage.py runserver

Frontend Setup:

->>cd frontend

->>npm install

->>npm run dev
______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

👨‍💻 Author

Ashwini Wakhare

Full Stack Python Developer (Django + React)
