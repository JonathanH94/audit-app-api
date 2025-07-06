# 📝 Audit Application API Demo
This is a FastAPI version of a [Django-based audit application prototype](https://github.com/JonathanH94/audit-app-django), built to demonstrate REST API functionality for internal audits. It is designed for technical teams evaluating modern backend solutions for replacing SharePoint-based auditing workflows.

---
## 🔍 Overview
This API provides endpoints to:
- 📋 Create, retrieve and edit questionnaire types
- ❓ Select questions associated with a questionnaire type
- 🧾 Perform CRUD operations on audit submissions
- 🧪 Access comprehensive API documentation and testing interfaces
---
## 💡 Purpose
This project serves as the **API backend** for an internal audit platform, intended to be paired with a frontend framework. The goal is to replace SharePoint lists with a modern, scalable system for conducting and tracking internal audits.

It also demonstrates **RESTful API design, type-safe validation**, and serves as a blueprint for larger audit or survey-based applications.

---
## ⚙️ Tech Summary
- **Framework**: FastAPI (Python)
- **API Documentation**: Interactive Swagger UI and ReDoc
- **Database**: SQLite (for demo/testing)
- **Validation**: Pydantic models for request/response validation
- **Testing**: Built-in testing client support
- **Async Handling**: Full async/await support
---
## 📎 Key Features
- 🛠️ RESTful API endpoints with full CRUD operations
- 🧪 Interactive API documentation available at `/docs` (Swagger) and `/redoc`
- ✅ Pydantic models ensure type safety and automatic validation
- 🔄 Async/await support for improved performance and scalability
---
## ⬆️ Improvements/Next Steps
- 🔐 Authentication via JWT and/or Microsoft 365 SSO (Azure AD OAuth2)
- 🛡️ Role-based access control (Admin, Contributor, Viewer, etc.)
- 🧩 Additional models and endpoints (e.g., question categories, users, teams)
- 🧠 Enhanced logic for dynamic questions/answers (e.g. multiple choice, reusable answer models)
- 🔍 Advanced search & filtering on submissions (e.g. by team, date, audit name)
- 🛢️ Database upgrade to **SQL Server** or **PostgreSQL** for production environments
- 🔁 API versioning and request throttling/rate limiting
- 🧑‍💻 Frontend integration with **React**, **Blazor**, or **Vue.js**


