# GSTEase - GST Return Filing Assistant

GSTEase is a modern web application designed to simplify GST return filing, purchase management, and invoice tracking.  
It provides a clean, responsive interface for businesses to manage their GST data efficiently.

---

## 🔗 Live URLs

- **Frontend (React SPA):** [https://gstease.onrender.com](https://gstease.onrender.com)  
- **Backend (Django API):** [https://gstease-backend.onrender.com](https://gstease-backend.onrender.com)

---

## 🧰 Tech Stack

- **Frontend:** React, Vite, CSS  
- **Backend:** Django 5, Django REST Framework, SQLite (for demo; PostgreSQL recommended for production)  
- **Deployment:** Render (Static Site + Web Service)  
- **Other:** Whitenoise for static files, CORS headers for cross-origin communication

---

## ⚡ Features

### 1. Purchase Management
- Create new purchases with unique purchase numbers and dates.  
- Add multiple items per purchase with automatic calculation of amount (`quantity × rate`).  
- Calculate GST automatically:
  - **CGST (9%)**  
  - **SGST (9%)**  
  - **IGST (if applicable)**  
- Edit and delete individual items or the entire purchase.  

### 2. Supplier Management
- Maintain supplier information including GSTIN, name, and address.  
- Autofill supplier details for recurring suppliers (future feature).  

### 3. Invoice & Tax Summary
- View a summary of all taxes and total amounts in a clean dashboard.  
- Subtotal, CGST, SGST, IGST, and total are updated in real-time.  

### 4. User Management & Authentication
- User registration and login (future: JWT-based authentication for API security).  
- Only authorized users can create or modify purchase records.  

### 5. Reporting & Export
- Generate PDF invoices and purchase reports using ReportLab (backend).  
- Export purchase data for accounting purposes (CSV/Excel).  

### 6. Frontend SPA Features
- Fully responsive design for desktop and mobile.  
- Dynamic routing for pages like Create Purchase, Invoice List, and Dashboard.  
- Smooth client-side navigation with React Router.  

### 7. Backend API
- RESTful API endpoints for all CRUD operations:
  - GET /api/purchases/ → List all purchases  
  - POST /api/purchase-create/ → Create a new purchase  
  - PUT /api/purchase/:id/ → Update a purchase  
  - DELETE /api/purchase/:id/ → Delete a purchase  
- API supports cross-origin requests from the frontend domain.  

### 8. Deployment & Scalability
- Backend deployed on **Render Web Service** with production-ready settings.  
- Frontend deployed on **Render Static Site** with SPA routing.  
- Easy to switch backend DB to PostgreSQL for production-grade deployments.  

---

## 🏗 Setup & Development

### 1. Frontend


cd gst-frontend
npm install
npm run dev
Build for production:

bash
Copy
Edit
npm run build
Push to GitHub and deploy on Render as a Static Site.

Ensure SPA routing by adding the rewrite rule:
/* → /index.html

2. Backend
   
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
Push to GitHub and deploy on Render as a Web Service.

Environment variables on Render:
SECRET_KEY → Use a secure secret key
DEBUG → False in production
