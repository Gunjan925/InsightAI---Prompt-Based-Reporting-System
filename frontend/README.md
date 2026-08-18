<!-- # React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project. -->


# InsightAI Frontend

A modern React-based frontend for the **InsightAI Prompt-Based Reporting System**.

The application allows users to securely upload structured datasets, generate AI-powered analytical reports using natural language prompts, visualize dataset statistics, manage report history, and configure user preferences through an intuitive dashboard.

The frontend communicates with the FastAPI backend through REST APIs and provides a responsive, production-ready user interface.

---

# Features

* User Registration & Login
* JWT Authentication
* Protected Routes
* Dataset Upload (CSV/XLS/XLSX)
* Upload Progress Tracking
* AI Prompt Input
* AI Report Generation
* HTML Report Viewer
* Report Download
* Report Printing (Save as PDF)
* Dashboard Analytics
* Report History
* Dark / Light Theme
* Toast Notifications
* Responsive Layout
* Error Handling
* Loading Indicators

---

# Tech Stack

| Technology       | Purpose                  |
| ---------------- | ------------------------ |
| React 19         | Frontend Framework       |
| Vite             | Development & Build Tool |
| React Router DOM | Client-side Routing      |
| Axios            | HTTP Client              |
| Tailwind CSS v4  | Styling                  |
| Recharts         | System Dashboard Charts  |
| React Plotly.js  | Dataset Visual Dashboards|
| Plotly.js        | Interactive Graph Engine |
| Lucide React     | Icons                    |
| React Hot Toast  | Notifications            |

---

# Folder Structure

```
frontend/
│
├── public/
│
├── src/
│
├── assets/
│   ├── images/
│   ├── icons/
│   └── logo/
│
├── components/
│   ├── Navbar.jsx
│   ├── Sidebar.jsx
│   ├── Loader.jsx
│   ├── PromptInput.jsx
│   ├── ReportViewer.jsx
│   │
│   ├── Upload/
│   │   ├── UploadButton.jsx
│   │   ├── UploadBox.jsx
│   │   └── UploadProgress.jsx
│   │
│   └── Charts/
│       ├── BarChart.jsx
│       ├── PieChart.jsx
│       ├── LineChart.jsx
│       └── ChartCard.jsx
│
├── pages/
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── Dashboard.jsx
│   ├── Upload.jsx
│   ├── DatasetDashboardPage.jsx
│   ├── Report.jsx
│   ├── History.jsx
│   └── Settings.jsx
│
├── context/
│   ├── AuthContext.jsx
│   └── ThemeContext.jsx
│
├── hooks/
│   └── useAuth.js
│
├── services/
│   ├── api.js
│   ├── auth.js
│   ├── upload.js
│   └── report.js
│
├── routes/
│   └── AppRoutes.jsx
│
├── styles/
│
├── utils/
│
├── App.jsx
├── main.jsx
└── index.css
```

---

# Installation

Clone the repository

```bash
git clone <repository-url>
```

Move into the project

```bash
cd frontend
```

Install dependencies

```bash
npm install
```

Start development server

```bash
npm run dev
```

Build for production

```bash
npm run build
```

Preview production build

```bash
npm run preview
```

---

# Environment Variables

Create a `.env` file.

```
VITE_API_URL=http://localhost:8000/api
```

Example Production

```
VITE_API_URL=https://your-domain.com/api
```

---

# Authentication

Authentication is handled using JWT tokens.

The frontend stores

* JWT Access Token
* User Information

inside browser Local Storage.

Every authenticated request automatically attaches

```
Authorization: Bearer <JWT Token>
```

using Axios interceptors.

If a request returns

```
401 Unauthorized
```

the session is automatically cleared and the user is redirected to Login.

---

# Application Routes

| Route                     | Description                      | Protected |
| ------------------------- | -------------------------------- | --------- |
| /login                    | User Login                       | No        |
| /register                 | User Registration                | No        |
| /dashboard                | Dashboard Overview               | Yes       |
| /upload                   | Upload Dataset & Prompts Wizard  | Yes       |
| /dashboard/view/:fileId   | Full-Screen Side-by-Side Dashboard| Yes       |
| /report/:id               | View Generated Report            | Yes       |
| /history                  | View Previous Reports            | Yes       |
| /settings                 | User Settings                    | Yes       |

---

# Components

## Navbar

Displays

* Application Logo
* Current User
* Theme Toggle
* Logout Button

---

## Sidebar

Provides navigation between pages.

Includes

* Dashboard
* Upload
* History
* Settings

---

## Loader

Reusable loading spinner.

Supports

* Inline Loading
* Full Page Loading

---

## PromptInput

Allows the user to enter natural language prompts that describe the desired analysis.

Example

```
Generate a sales summary.

Show yearly trends.

Find anomalies.

Compare regional performance.
```

---

## UploadButton

Provides

* Drag and Drop Upload
* File Browser
* File Validation
* Size Validation
* Extension Validation

Supported Files

* CSV
* XLS
* XLSX

---

## UploadProgress

Displays

* Upload Percentage
* Progress Bar
* Upload Status

---

## ReportViewer

Displays generated HTML reports.

Supports

* Embedded HTML Rendering
* Download Report
* Print Report

---

## Charts

Dashboard visualizations built using Recharts.

Includes

* Bar Chart
* Pie Chart
* Line Chart
* Chart Card Wrapper

---

# Pages

## Login

Allows users to authenticate.

Features

* Email Validation
* Password Validation
* Show/Hide Password
* Error Messages
* Loading Indicator

---

## Register

Allows creation of new accounts.

Automatically logs the user in after successful registration.

---

## Dashboard

Displays

* Total Uploads
* Generated Reports
* File Type Distribution
* Recent Activity
* Dashboard Charts

---

## Upload

Main AI workflow page.

Steps

1. Upload Dataset
2. Enter Prompt
3. Generate AI Report

---

## Report

Displays AI-generated report.

Supports

* HTML Rendering
* Download
* Print

---

## History

Displays all reports previously generated by the logged-in user.

Supports

* View Report
* Download Report
* Delete Report

---

## Settings

Allows users to

* View Username
* View Email
* Change Theme
* Change Password (when backend support is added)
* Logout
* Delete Account (when backend support is added)

---

# Services

## api.js

Creates a reusable Axios instance.

Responsibilities

* Base URL configuration
* JWT attachment
* Global error handling
* Unauthorized session cleanup

---

## auth.js

Handles

* Login
* Register
* Logout

---

## upload.js

Handles dataset uploads.

Supports upload progress callbacks.

---

## report.js

Handles

* Generate Report
* Fetch Report
* Download Report
* Dashboard Statistics
* History

---

# Backend API Endpoints Used

## Authentication

| Method | Endpoint       | Description   |
| ------ | -------------- | ------------- |
| POST   | /auth/register | Register User |
| POST   | /auth/login    | Login User    |
| POST   | /auth/logout   | Logout User   |

---

## Upload

| Method | Endpoint | Description                          |
| ------ | -------- | ------------------------------------ |
| POST   | /upload  | Upload Dataset                       |
| GET    | /upload  | Fetch Previously Uploaded Datasets   |

---

## Reports

| Method | Endpoint              | Description          |
| ------ | --------------------- | -------------------- |
| POST   | /report/generate      | Generate AI Report   |
| GET    | /report/{id}          | Get Report           |
| GET    | /report/{id}/download | Download HTML Report |

---

## Dashboard

| Method | Endpoint                    | Description                              |
| ------ | --------------------------- | ---------------------------------------- |
| GET    | /dashboard/stats            | Dashboard Statistics Overview            |
| GET    | /dashboard/generate/{file_id}| Generate & Retrieve Visual Plotly Charts |

---

## History

| Method | Endpoint      | Description         |
| ------ | ------------- | ------------------- |
| GET    | /history      | User Report History |
| DELETE | /history/{id} | Delete Report       |

---

# Upload Workflow (Two-Phase Flow)

```
[Phase 1: Dataset Upload & Visual Insights]
Select Dataset (Upload new CSV/Excel OR Select from Database History)
        │
        ▼
Upload/Validate File ID
        │
        ▼
Click "Generate Visual Dashboard"
        │
        ▼
Launches Full Dashboard in a New Browser Tab (GET /api/dashboard/generate/:fileId)
Renders Side-by-Side Plots (Bar, Scatter, Pie, Heatmap, Lines) Natively

[Phase 2: Natural Language Report Generation]
Go back to Upload Wizard Tab
        │
        ▼
Enter Natural Language Prompt describing report context
        │
        ▼
Click "Generate AI Report"
        │
        ▼
Backend triggers AI service RAG / Gemini analysis
        │
        ▼
Generated Report Saved to MySQL
        │
        ▼
Redirect to /report/:id (Interactive HTML viewer)
```

---

# Security

The frontend includes several security practices.

* Protected Routes
* JWT Authentication
* Automatic Session Expiration
* File Type Validation
* File Size Validation
* Axios Interceptors
* Environment Variables
* No Backend URLs Hardcoded
* HTML reports rendered only from trusted backend-generated content

---

# Theme Support

Supports

* Light Mode
* Dark Mode

Implemented using

* CSS Variables
* Tailwind CSS
* Theme Context
* Local Storage Persistence

---

# Responsive Design

Optimized for

* Desktop
* Laptop
* Tablet
* Mobile Devices

---