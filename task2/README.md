# Arithmetic API TASK-2

A simple REST API built with **Django** and **Django REST Framework** that performs basic arithmetic operations (addition, subtraction, multiplication, division) on two numbers.

Each API endpoint accepts **two numbers as parameters** and returns the result of the corresponding arithmetic operation.

---

## Features

* **REST API Design**: Clean and predictable endpoint structure.
* **Arithmetic Operations**: Support for basic math logic.
* **Security**: Environment variable support using `.env` for sensitive configurations.
* **Authentication**: JWT-based user registration and login.

---

## Tech Stack

* **Python**
* **Django**
* **Django REST Framework**
* **python-dotenv**

---

## Project Structure

```text
backend-assignment/
│
├── task1/
└── task2/
    ├── calculator/
    │   ├── views.py
    │   ├── urls.py
    │   ├── models.py
    │   ├── services.py
    │   ├── tests.py
    │   └── serializers.py
    ├── config/
    │   ├── settings.py
    │   └── urls.py
    ├── .env.example
    ├── manage.py
    └── requirements.txt

```

---

# Installation & Setup

### 1 Clone the repository

```bash
git clone <repository-url>
cd <backend-assignment/task2>
```

### 2 Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3 Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

This project uses environment variables for sensitive settings.

1. Copy the example environment file:

```bash
cp .env-example .env
```

# Run the Project

Apply migrations:

```bash
python manage.py migrate
```

Start the server:

```bash
python manage.py runserver
```

Server runs at:

```
http://127.0.0.1:8000
```

---

# API Endpoints

<details>
<summary><strong>Authentication</strong></summary>

### Register

```
POST /api/register/
Body :
{
    "username": "test_user",
    "email": "testemail@gmail.com",
    "first_name": "your_first_name",
    "last_name": "your_last_name",
    "password": "your_password",
    "password_confirm": "your_password"
}
```

### Login

```
POST /api/login/
Body :
{
    "username": "test_user",
    "password": "your_password"
}
```



### Token Refresh

```
POST /api/refresh/
Body :
{
    "refresh": "your_refresh_token"
}
```


### Logout

```
POST /api/logout/
Body :
{
    "refresh": "your_refresh_token"
}
```


</details>

<details>
<summary><strong>Arithmetic Operations</strong></summary>

## Addition
```
GET /api/calculate/sum/<num1>/<num2>/
```

## Subtraction
```
GET /api/calculate/difference/<num1>/<num2>/
```

## Division
```
GET /api/calculate/divide/<num1>/<num2>/
```

## Multiplication
```
GET /api/calculate/multiply/<num1>/<num2>/
```

</details>

# Security Notes

* `.env` file is excluded from version control.
* `.env.example` provides the required environment variables.

---

# Author

Ashwin Sanalkumar

---
