# SubWrite — Full-Stack Content Publishing Platform

SubWrite is a full-stack blogging and content publishing platform that allows writers to create, publish, and manage markdown-based articles while enabling readers to discover, engage, and interact with content through social features.

The project demonstrates real-world backend architecture including authentication systems, email workflows, dynamic server-rendered UI, and production-ready deployment.

---

## 🌐 Live Demo

https://subwrite.onrender.com

---

##  Core Capabilities

###  Authentication & Accounts
- Secure user registration and login  
- JWT-based authentication using HTTP-only cookies  
- Email verification workflow  
- Password reset via email  
- Secure password hashing with bcrypt  

---

###  Content Management
- Create, edit, and delete articles  
- Draft and publish workflow  
- Writer dashboard for managing posts  
- Markdown editor with live preview  

---

###  Discovery & Engagement
- Tag and category system  
- Full-text article search  
- Likes and comment system  
- Follow writers  
- Personalized feed of followed creators  

---

###  User Profiles
- Public creator profiles  
- Bio and social links (GitHub, Twitter, website)  
- Profile images  
- Article counts and listings  

---

###  Email System
- SMTP-based transactional emails  
- Welcome email for new users  
- Email verification links  
- Secure password reset flow  

---

###  UI & User Experience
- Responsive modern UI  
- Server-rendered templates using HTMX  
- Dynamic partial updates without full page reload  
- Clean typography and navigation  

---

##  Engineering Highlights

- JWT authentication with HTTP-only cookies  
- Secure token generation for verification and password reset  
- SQLAlchemy ORM relational database modeling  
- Modular FastAPI project architecture  
- Environment-based configuration using `.env`  
- Docker containerization for deployment  
- Production deployment on Render  

---

##  Tech Stack

**Backend**
- FastAPI  
- SQLAlchemy  
- Python  

**Frontend**
- HTMX  
- Jinja2 Templates  
- Tailwind CSS  

**Infrastructure**
- Docker  
- SMTP (Gmail)  
- Render Deployment  

---

##  Local Development Setup

###  1. Clone repository

```bash
git clone https://github.com/yourusername/subwrite.git
cd subwrite
```

###  2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
```
for windows
```bash
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a .env file in the project root:
```bash
SECRET_KEY=your_secret_key
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
BASE_URL=http://localhost:8000
```

### 5. Run the application
```bash
uvicorn app.main:app --reload
```

---

## Running with Docker
Build the container:
```bash
docker build -t subwrite .
```
Run the container:
```bash
docker run -p 8000:8000 subwrite
```
Open:
```bash
http://localhost:8000
```

---

## Future Improvement
- Recommendation engine for personalized content
- Creator analytics dashboard
- Payment / tipping system for writers
- Draft version history