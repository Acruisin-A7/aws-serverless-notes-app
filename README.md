# Serverless Notes Application (AWS)

A fully serverless, end-to-end CRUD notes application built entirely within the AWS Free Tier using **only the AWS Management Console** (no SAM, CDK, Terraform, or CLI).  
The project demonstrates a complete request-driven serverless architecture with a real frontend, API layer, database, and access control logic.

---

## 🔗 Live Demo

**Frontend (S3 static hosting):**  
https://notes-app-frontend7.s3.ap-south-1.amazonaws.com/index.html

> Notes are isolated per browser/device. Opening the app in incognito or on another device will show a separate (empty) notes list.

---

## 🏗️ Architecture Overview

**Frontend**
- Static single-page application built with **plain HTML, CSS, and vanilla JavaScript**
- Hosted on **Amazon S3** using static website hosting

**Backend**
- **Amazon API Gateway (HTTP API)** exposing RESTful endpoints
- **Single AWS Lambda function (Python)** handling all routes and business logic
- **Amazon DynamoDB** single-table design with a **Global Secondary Index (GSI)**

**Observability & Security**
- **Amazon CloudWatch Logs** for Lambda execution and errors
- **Least-privilege IAM role** scoped only to required DynamoDB actions
- No hardcoded credentials or secrets

---

## 🔄 Data Flow

1. User interacts with the frontend hosted on S3  
2. Frontend sends HTTP requests to API Gateway  
3. API Gateway routes requests to a single Lambda function  
4. Lambda performs validation and business logic  
5. Data is stored/retrieved from DynamoDB  
6. Lambda returns JSON responses to the frontend  

---

## ✨ Key Features

- Full CRUD functionality:
  - Create notes
  - List notes
  - View a single note
  - Update notes
  - Delete notes
- **Per-device data isolation**
  - Each browser/device has its own private notes
  - Implemented using a client-generated `device_id`
- Persistent data across page refreshes on the same device
- Explicit CORS handling for a static frontend
- Publicly accessible live demo

---

## 🧠 Design Decisions & Evolution

This project intentionally evolved beyond a naive CRUD implementation:

### API Design
- Started with a single proxy route
- Switched to **explicit REST routes** for clarity and maintainability:
  - `POST /notes`
  - `GET /notes`
  - `GET /notes/{id}`
  - `PUT /notes/{id}`
  - `DELETE /notes/{id}`

### DynamoDB Modeling
- Initial approach: `Scan` on the table (global visibility)
- Final approach:
  - Added `device_id` attribute
  - Introduced a **Global Secondary Index (GSI)** on `device_id`
  - Replaced scans with `Query` operations for efficient, scoped reads

### Data Isolation (Without Authentication)
- No Cognito or user accounts (by design)
- Each client generates and persists a `device_id` in `localStorage`
- Backend enforces ownership checks on all read/update/delete operations
- This provides isolation without adding authentication complexity

### CORS Handling
- Explicit `OPTIONS` handling in Lambda
- Proper CORS headers returned on every response
- Enables clean integration with S3 static hosting

---

## 🔐 Security Considerations

- IAM role follows **principle of least privilege**
- Lambda can access **only** the required DynamoDB table and its indexes
- No credentials, secrets, or account-specific identifiers are committed to GitHub
- S3 bucket policy allows **public read only** for frontend assets
- Backend access is controlled exclusively via IAM

> Note: Bucket policies and environment-specific infrastructure wiring are intentionally not committed to GitHub.

---

## 💰 Cost Awareness

- Fully serverless architecture (no always-on resources)
- Designed to remain within the **AWS Free Tier**
- DynamoDB on-demand capacity
- No EC2, no RDS, no load balancers

---

## 🧪 Error Handling & Observability

- Clear distinction between client errors (400), not found (404), and server errors (500)
- Structured logging in Lambda
- CloudWatch used for debugging and monitoring execution behavior

---


## 🚀 Possible Improvements

- Add authentication using Amazon Cognito
- Add pagination to list endpoints
- Infrastructure-as-Code using AWS SAM or CDK
- Environment-based configuration for frontend API URL

---

## 👤 Author

Arun  
B.Sc. IT Graduate | AWS & Backend Enthusiast

---

## 📌 Final Notes

This project focuses on **correct architecture, clean API design, proper DynamoDB access patterns, and realistic trade-offs**, rather than overengineering.  
It is intended to demonstrate practical AWS fundamentals in a production-like serverless application.


