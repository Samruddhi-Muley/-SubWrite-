# SubWrite — Full-Stack Content Publishing Platform

SubWrite is a full-stack blogging and content publishing platform that enables writers to create, publish, and manage markdown-based articles with social engagement and email-driven workflows.

The project demonstrates production-style backend architecture, authentication systems, dynamic server-rendered UI, and creator-focused features.

---

##  Core Capabilities

### 🔐 Authentication & Accounts
- Secure user registration and login  
- JWT-based session authentication  
- Email verification and password reset workflows  
- Argon2 password hashing  

---

### ✍️ Content Management
- Create, edit, delete articles  
- Draft and publish lifecycle  
- Writer dashboard  
- Markdown editor with live preview  

---

### 🔍 Discovery & Engagement
- Tag and category system  
- Search by title, content, and author  
- Likes, comments, follow system  
- Personalized content feed  

---

### 👤 User Profiles
- Public creator profiles  
- Bio and social links  
- Profile images  
- Article listing and counts  
- Verified badge support  

---

### 📧 Email Infrastructure
- SMTP-based transactional emails  
- Welcome emails  
- Account verification  
- Password recovery  

---

### 🎨 UI & Experience
- Responsive, modern UI  
- Server-rendered templates with dynamic updates  
- Clean typography and navigation  

---

## 🧠 Engineering Highlights

- JWT authentication using HTTP-only cookies  
- Asynchronous email delivery  
- Relational data modeling with SQLAlchemy  
- HTMX-powered partial page updates  
- Modular FastAPI architecture  
- Secure credential handling via environment variables  

---

## 🛠 Tech Stack

- FastAPI  
- SQLAlchemy  
- HTMX  
- Jinja2  
- Tailwind CSS  
- SMTP (Gmail)  

---

## ⚙️ Local Setup

Clone the repository:
```bash
git clone https://github.com/yourusername/subwrite.git
cd subwrite
```
Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Configure environment variables: Create a .env file:
```bash
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///subwrite.db
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```
Run the app:
```bash
uvicorn main:app --reload
```
Open browser:
```bash
http://localhost:8000
```