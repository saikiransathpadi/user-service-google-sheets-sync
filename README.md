# User Management Service with Google Sheets Sync

A FastAPI-based backend service that provides user management capabilities with Google Sheets synchronization. This project demonstrates integration with Google OAuth 2.0, MongoDB, and Google Sheets API.


## Features

- **Google OAuth 2.0 Authentication**: User authentication using Google accounts
- **User Management**: Complete CRUD operations for managing users
- **Pagination Support**: Data retrieval with custom pagination
- **Google Sheets Integration**:
  - Create Google Sheets programmatically
  - Sync data from MongoDB to Google Sheets
  - Import data from Google Sheets to MongoDB
- **MongoDB Database**: NoSQL database with async support using Motor
- **RESTful API**: Clean, well-documented API endpoints
- **Docker Support**: Fully containerized application ready for deployment
- **Unit Tests**: Comprehensive test coverage using pytest
- **Postman Collection**: Pre-configured API collection for easy testing


## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10 or higher
- MongoDB (local or cloud instance)
- Docker and Docker Compose (optional, for containerized setup)
- Google Cloud Console account (for OAuth credentials)

## Google Cloud Setup

1. **Create a Google Cloud Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Required APIs**
   - Go to "APIs & Services" > "Library"
   - Enable the following APIs:
     - Google Sheets API
     - Google Drive API
     - Google+ API (for OAuth)

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URI: `http://localhost:8003/auth/callback`
   - Save your Client ID and Client Secret

## Installation & Setup

### Option 1: Local Setup (Without Docker)

#### Step 1: Clone the Repository

```bash
cd backend
```

#### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
MONGODB_URI=mongodb://localhost:27017/user_management
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
OAUTH_REDIRECT_URL=http://localhost:8003/auth/callback
SECRET_KEY=your-secret-key-for-jwt-change-in-production
```

#### Step 5: Start MongoDB

Ensure MongoDB is running on your local machine:

```bash
# On Linux/Mac
sudo systemctl start mongod

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

#### Step 6: Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8003`

API Documentation (Swagger UI): `http://localhost:8003/docs`

### Option 2: Docker Setup (Recommended for Production)

#### Step 1: Configure Environment Variables

Create a `.env` file in the backend directory with your credentials (see Step 4 above).

#### Step 2: Build and Run with Docker Compose

```bash
docker-compose up --build
```

This will:
- Start MongoDB container
- Build and start the FastAPI application
- Configure networking between containers

The API will be available at: `http://localhost:8003`

#### Step 3: Stop the Containers

```bash
docker-compose down

# To remove volumes as well
docker-compose down -v
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/auth/login` | Initiate Google OAuth flow | No |
| GET | `/auth/callback` | Handle OAuth callback | No |
| GET | `/auth/me` | Get current user info | No |

### User Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users` | Get all users (paginated) | Yes |
| GET | `/users/{id}` | Get user by ID | Yes |
| POST | `/users` | Create a new user | Yes |
| PUT | `/users/{id}` | Update user | Yes |
| DELETE | `/users/{id}` | Delete user | Yes |

### Google Sheets Sync Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/sync/create-sheet` | Create a new Google Sheet | Yes |
| POST | `/sync/{sheet_id}/to-cloud` | Sync DB → Google Sheets | Yes |
| POST | `/sync/{sheet_id}/from-cloud` | Sync Google Sheets → DB | Yes |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health status |
| GET | `/` | API information |

## Using the API

### Step 1: Authentication Flow

1. **Initiate OAuth Login**
   ```bash
   curl http://localhost:8003/auth/login
   ```

   Response will contain `authorization_url`. Open this URL in your browser.

2. **Complete Google Authentication**
   - Sign in with your Google account
   - Grant the requested permissions
   - You'll be redirected to the callback URL

3. **Get Your Access Token**
   The callback will return your user email as the access token. Use this email in the `Authorization` header for subsequent requests.

### Step 2: Create Users

```bash
curl -X POST http://localhost:8003/users \
  -H "Authorization: Bearer your-email@gmail.com" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "role": "Developer"
  }'
```

### Step 3: Get All Users (with Pagination)

```bash
curl -X GET "http://localhost:8003/users?page=1&page_size=10" \
  -H "Authorization: Bearer your-email@gmail.com"
```

### Step 4: Create a Google Sheet

```bash
curl -X POST http://localhost:8003/sync/create-sheet \
  -H "Authorization: Bearer your-email@gmail.com" \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_name": "My User Management Sheet"
  }'
```

Save the returned `sheet_id` for sync operations.

### Step 5: Sync to Google Sheets

```bash
curl -X POST http://localhost:8003/sync/{sheet_id}/to-cloud \
  -H "Authorization: Bearer your-email@gmail.com"
```

### Step 6: Sync from Google Sheets

```bash
curl -X POST http://localhost:8003/sync/{sheet_id}/from-cloud \
  -H "Authorization: Bearer your-email@gmail.com"
```

## Using Postman Collection

A complete Postman collection is included in `postman_collection.json`.

### Import into Postman

1. Open Postman
2. Click "Import" button
3. Select `postman_collection.json`
4. The collection will be imported with all endpoints

### Configure Variables

After import, update the collection variables:

- `base_url`: `http://localhost:8003` (default)
- `auth_token`: Your authenticated user email (set after OAuth login)
- `user_id`: Auto-populated after creating a user
- `sheet_id`: Auto-populated after creating a sheet

### Authentication Flow in Postman

1. Run "Initiate Google OAuth Login" request
2. Copy the `authorization_url` from response
3. Open URL in browser and complete authentication
4. Copy the `access_token` (email) from the callback response
5. Update the collection variable `auth_token` with your email
6. All subsequent requests will use this token automatically

## Running Tests

The project includes comprehensive unit tests.

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=app --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

### Run Specific Test File

```bash
pytest tests/test_users.py
pytest tests/test_auth.py
```

### Run Tests in Docker

```bash
docker-compose run api pytest
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration and settings
│   ├── database.py            # MongoDB connection and setup
│   ├── models.py              # Pydantic models and schemas
│   ├── auth.py                # Google OAuth implementation
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User CRUD endpoints
│   │   └── sync.py            # Google Sheets sync endpoints
│   └── services/
│       ├── __init__.py
│       └── sheets_service.py  # Google Sheets integration logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── test_auth.py           # Authentication tests
│   └── test_users.py          # User management tests
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image configuration
├── docker-compose.yml         # Multi-container setup
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── pytest.ini                 # Pytest configuration
├── postman_collection.json    # Postman API collection
└── README.md                  # This file
```

## Database Schema

### Users Collection

```javascript
{
  "_id": ObjectId,           // MongoDB ObjectId
  "name": String,            // User's full name
  "email": String,           // User's email (unique)
  "role": String,            // User's role
  "created_at": DateTime     // Creation timestamp
}
```

### Authenticated Users Collection

```javascript
{
  "_id": ObjectId,
  "email": String,           // User's email (unique)
  "name": String,            // User's name from Google
  "profile_pic": String,     // Google profile picture URL
  "access_token": String,    // Google OAuth access token
  "refresh_token": String,   // Google OAuth refresh token
  "created_at": DateTime,
  "updated_at": DateTime
}
```

## Google Sheets Structure

When you create a sheet or sync data, the Google Sheet will have the following structure:

| ID | Name | Email | Role | Created At |
|----|------|-------|------|------------|
| 671b1234abc567890 | John Doe | john@example.com | Developer | 2025-10-25 12:00:00 |

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Resource deleted successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a detailed message:

```json
{
  "detail": "Error description here"
}
```
