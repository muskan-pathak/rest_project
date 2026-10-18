# Custom User Management & Authentication API

A Django REST Framework project for user management and authentication.
It includes a custom user model based on Django's AbstractUser, user
CRUD endpoints, soft deletion, JWT login, email OTP verification,
password reset flows, and welcome emails.

# Features

-   Custom `User` model extending `AbstractUser`
-   Unique email address and profile/status choices
-   User create, list, retrieve, update, and soft-delete APIs
-   Password hashing through Django's password utilities
-   JWT login using Simple JWT
-   Email OTP generation and verification with a five-minute expiry
-   Forgot-password and reset-password flow using OTP
-   Welcome email after successful user creation


# Technology Stack

Python
Django
Django REST Framework
Simple JWT
Pillow 
`python-dotenv` (for environment variables)
 SMTP email (Gmail configuration shown below)

# Project Structure

The project uses the Django project package `user_model` and the apps
`users` and `users_authentication`.

``` text
rest_project/
├── manage.py
├── user_model/
│   ├── settings.py
│   └── urls.py
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── users_authentication/
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── .env               
├── .gitignore
└── requirements.txt
```


# Prerequisites

-   Python 3 installed
-   Git
-   Postman
-   A Gmail account and a Google App Password if using Gmail SMTP

#Setup Instructions

### 1. Clone the repository

``` bash
git clone https://github.com/muskan-pathak/rest_project.git
cd rest_project
```

### 2. Create and activate a virtual environment

On macOS/Linux:

``` bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

# 3. Install dependencies



``` bash
pip install -r requirements.txt
```


# 4. Configure environment variables

Create a `.env` file in the same directory as `manage.py`. Do not commit
this file to GitHub.

Example:

``` dotenv
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_character_google_app_password
```

Use a Google App Password for SMTP where required; do not put your
normal Gmail password in the file. Keep the values private.

The email settings in `user_model/settings.py` should read these values,
for example:

``` python
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

Make sure `python-dotenv` is installed if you use `load_dotenv()`. If
your project uses a different email provider, configure its SMTP
settings instead.

### 5. Check Django settings

Confirm that the custom user model is configured in
`user_model/settings.py`:

``` python
AUTH_USER_MODEL = "users.User"
```

Confirm that Django REST Framework uses Simple JWT authentication if the
project is configured for JWT-protected endpoints:

``` python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
```

# 6. Create and apply migrations

Run these commands from the directory containing `manage.py`:


python3 manage.py makemigrations
python3 manage.py migrate


If your virtual environment uses `python` instead of `python3`, you can
use `python manage.py ...`.

If you have just added or changed fields in the `User` model, create and
apply the relevant migrations before testing the APIs.

# 7. Create an admin user (optional)

``` bash
python3 manage.py createsuperuser
```


# 8. Run the development server

``` bash
python3 manage.py runserver
```

The local API base URL is:

``` text
http://127.0.0.1:8000/
```

Keep the server running while testing with Postman.

## API Usage


  ------------------------------------------------------------------------------
  Method                  Endpoint                       Purpose
  ----------------------- ------------------------------ -----------------------
  `POST`                  `/api/users/`                  Create a user and send
                                                         a welcome email

  `GET`                   `/api/users/`                  List active users

  `GET`                   `/api/users/<id>/`             Retrieve one user's
                                                         details

  `PUT`                   `/api/users/<id>/`             Full update; send all
                                                         required fields

  `PATCH`                 `/api/users/<id>/`             Partial update; send
                                                         only fields to change

  `DELETE`                `/api/users/<id>/`             Soft-delete a user by
                                                         setting status to
                                                         `Inactive`

  `POST`                  `/api/auth/login/`             Log in with email and
                                                         password; receive JWT
                                                         tokens

  `POST`                  `/api/auth/send-otp/`          Generate and email an
                                                         OTP

  `POST`                  `/api/auth/verify-otp/`        Verify an OTP

  `POST`                  `/api/auth/forgot-password/`   Send a password-reset
                                                         OTP

  `POST`                  `/api/auth/reset-password/`    Reset a password after
                                                         OTP verification
  ------------------------------------------------------------------------------

### User CRUD examples

# Create a user

`POST http://127.0.0.1:8000/api/users/`

Choose **Body → raw → JSON** in Postman and send the fields required by
your serializer. Example:

``` json
{
  "username": "sampleuser",
  "password": "ChooseAStrongPassword123!",
  "first_name": "Sample",
  "last_name": "User",
  "email": "sample.user@example.com",
  "profiles": "Standard",
  "gender": "Other",
  "nationality": "Indian",
  "blood_group": "O+",
  "phone": "9876543210",
  "permanent_address": "Sample permanent address",
  "current_address": "Sample current address",
  "emergency_contact_name": "Emergency Contact",
  "emergency_contact_number": "9876501234",
  "emergency_contact_relationship": "Parent",
  "status": "Active"
}
```
This is only example include unique email and username


# Retrieve a user

`GET http://127.0.0.1:8000/api/users/1/`

Replace 1 with user ID


#Update a user with PATCH

`PATCH http://127.0.0.1:8000/api/users/1/`

Example body:

``` json
{
  "phone": "155555556"
}
```
patch is for partial change 


#Update a user with PUT

`PUT http://127.0.0.1:8000/api/users/1/`

PUT is intended for a full update. Send all fields required by your
serializer. If the serializer marks `password` as required for PUT, it
may reject the request when password is omitted. Ensure password updates
are handled securely and hashed rather than stored as plain text.

# Soft-delete a user

`DELETE http://127.0.0.1:8000/api/users/1/`

The project should change the user's status to `Inactive` instead of
deleting the database row. The API's active-only list should then omit
that user.

# Login and JWT usage

`POST http://127.0.0.1:8000/api/auth/login/`

by sending email and password returns accdss token 

For endpoints configured to require authentication, use the **access
token** in Postman:

1.  Open the request's **Authorization** tab.
2.  Select **Bearer Token**.
3.  Paste the access token returned by login.
4.  Send the request.

The header format is:

``` text
Authorization: Bearer <access_token>
```

Do not send the refresh token as the normal API access token. JWT
authentication settings alone do not make every endpoint protected;
permissions on each view determine whether authentication is required.

# OTP and password reset flow

Use the request fields defined in your current serializers. The usual
flow is:

1.  `/api/auth/send-otp/` to request an email OTP.
2.  `/api/auth/verify-otp/` with the email and OTP fields expected
    by the serializer.
3.  For a forgotten password, call `/api/auth/forgot-password/`.
4.  Use the reset OTP with `/api/auth/reset-password/` and the new
    password field expected by your serializer.

it uses 5 minutes OTP expiry sent by email.expired incorect and already used OTP should be rejected

# Testing with Postman

1.  Start the Django development server.
2.  Open your saved Postman collection.
3.  Test user creation and confirm the welcome email is received.
4.  Test list, retrieve, PUT, PATCH, and soft-delete operations.
5.  Test login and save the access token from the response.
6.  Test OTP verification and password reset, including invalid or
    expired OTP cases.
7.  If a protected endpoint is configured, test it with a valid access
    token and without a token.

Expected status codes depend on the view implementation. Common results
include `200 OK` for successful reads/updates, `201 Created` for
successful creation, `400 Bad Request` for validation errors,
`401 Unauthorized` for missing/invalid authentication on protected
endpoints, and `404 Not Found` for a user that cannot be found.



