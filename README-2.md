# Custom User Management & Authentication API**



A Django REST Framework project for user management and authentication.

It includes a custom user model based on Django's AbstractUser, user

CRUD endpoints, soft deletion, JWT login, email OTP verification,

password reset flows, and welcome emails.



**# Features**



\-   Custom \`User\` model extending \`AbstractUser\`

\-   Unique email address and profile/status choices

\-   User create, list, retrieve, update, and soft-delete APIs

\-   Password hashing through Django's password utilities

\-   JWT login using Simple JWT

\-   Email OTP generation and verification with a five-minute expiry

\-   Forgot-password and reset-password flow using OTP

\-   Welcome email after successful user creation
\-   Client management API with authenticated CRUD operations and audit tracking





# Technology Stack



Python

Django

Django REST Framework

Simple JWT

Pillow&#x20;

\`python-dotenv\` (for environment variables)

&#x20;SMTP email (Gmail configuration shown below)



**# Project Structure**



The project uses the Django project package \`user_model\` and the apps

\`users\` and \`users_authentication\`.



\`\`\` text

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

├── .env              &#x20;

├── .gitignore

└── requirements.txt

\`\`\`





**# Prerequisites**



\-   Python 3 installed

\-   Git

\-   Postman

\-   A Gmail account and a Google App Password if using Gmail SMTP



\#Setup Instructions



1. Clone the repository



\`\`\` bash

git clone https\://github.com/muskan-pathak/rest_project.git

cd rest_project

\`\`\`



**### 2. Create and activate a virtual environment**



On macOS/Linux:



\`\`\` bash

python3 -m venv venv

source venv/bin/activate

\`\`\`



On Windows:



\`\`\` bash

python -m venv venv

venv\Scripts\activate

\`\`\`



*# 3. Install dependencies**







\`\`\` bash

pip install -r requirements.txt

\`\`\`





**# 4. Configure environment variables**



Create a \`.env\` file in the same directory as \`manage.py\`. Do not commit

this file to GitHub.



Example:



\`\`\` dotenv

EMAIL_HOST_USER=your_email\@gmail.com

EMAIL_HOST_PASSWORD=your_16_character_google_app_password

\`\`\`



Use a Google App Password for SMTP where required; do not put your

normal Gmail password in the file. Keep the values private.



The email settings in \`user_model/settings.py\` should read these values,

for example:



\`\`\` python

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

\`\`\`



Make sure \`python-dotenv\` is installed if you use \`load_dotenv()\`. If

your project uses a different email provider, configure its SMTP

settings instead.



**### 5. Check Django settings**



Confirm that the custom user model is configured in

\`user_model/settings.py\`:



\`\`\` python

AUTH_USER_MODEL = "users.User"

\`\`\`



Confirm that Django REST Framework uses Simple JWT authentication if the

project is configured for JWT-protected endpoints:



\`\`\` python

REST_FRAMEWORK = {

&#x20;   "DEFAULT_AUTHENTICATION_CLASSES": (

&#x20;       "rest_framework_simplejwt.authentication.JWTAuthentication",

&#x20;   ),

}

\`\`\`



**# 6. Create and apply migrations**



Run these commands from the directory containing \`manage.py\`:





python3 manage.py makemigrations

python3 manage.py migrate





If your virtual environment uses \`python\` instead of \`python3\`, you can

use \`python manage.py ...\`.



If you have just added or changed fields in the \`User\` model, create and

apply the relevant migrations before testing the APIs.



**# 7. Create an admin user (optional)**



\`\`\` bash

python3 manage.py createsuperuser

\`\`\`





**# 8. Run the development server**



\`\`\` bash

python3 manage.py runserver

\`\`\`



The local API base URL is:



\`\`\` text

http\://127.0.0.1:8000/

\`\`\`



Keep the server running while testing with Postman.



**## API Usage**





**&#x20; ------------------------------------------------------------------------------**

&#x20; Method                  Endpoint                       Purpose

**&#x20; ----------------------- ------------------------------ -----------------------**

&#x20; \`POST\`                  \`/api/users/\`                  Create a user and send

&#x20;                                                        a welcome email



&#x20; \`GET\`                   \`/api/users/\`                  List active users



&#x20; \`GET\`                   \`/api/users/\<id>/\`             Retrieve one user's

&#x20;                                                        details



&#x20; \`PUT\`                   \`/api/users/\<id>/\`             Full update; send all

&#x20;                                                        required fields



&#x20; \`PATCH\`                 \`/api/users/\<id>/\`             Partial update; send

&#x20;                                                        only fields to change



&#x20; \`DELETE\`                \`/api/users/\<id>/\`             Soft-delete a user by

&#x20;                                                        setting status to

&#x20;                                                        \`Inactive\`



&#x20; \`POST\`                  \`/api/auth/login/\`             Log in with email and

&#x20;                                                        password; receive JWT

&#x20;                                                        tokens



&#x20; \`POST\`                  \`/api/auth/send-otp/\`          Generate and email an

&#x20;                                                        OTP



&#x20; \`POST\`                  \`/api/auth/verify-otp/\`        Verify an OTP



&#x20; \`POST\`                  \`/api/auth/forgot-password/\`   Send a password-reset

&#x20;                                                        OTP



&#x20; \`POST\`                  \`/api/auth/reset-password/\`    Reset a password after

&#x20;                                                        OTP verification

&#x20; \------------------------------------------------------------------------------



**### User CRUD examples**



**# Create a user**



\`POST http\://127.0.0.1:8000/api/users/\`



Choose **\*\*Body → raw → JSON\*\*** in Postman and send the fields required by

your serializer. Example:



\`\`\` json

{

&#x20; "username": "sampleuser",

&#x20; "password": "ChooseAStrongPassword123!",

&#x20; "first_name": "Sample",

&#x20; "last_name": "User",

&#x20; "email": "sample.user\@example.com",

&#x20; "profiles": "Standard",

&#x20; "gender": "Other",

&#x20; "nationality": "Indian",

&#x20; "blood_group": "O+",

&#x20; "phone": "9876543210",

&#x20; "permanent_address": "Sample permanent address",

&#x20; "current_address": "Sample current address",

&#x20; "emergency_contact_name": "Emergency Contact",

&#x20; "emergency_contact_number": "9876501234",

&#x20; "emergency_contact_relationship": "Parent",

&#x20; "status": "Active"

}

\`\`\`

This is only example include unique email and username





**# Retrieve a user**



\`GET http\://127.0.0.1:8000/api/users/1/\`



Replace 1 with user ID





\#Update a user with PATCH



\`PATCH http\://127.0.0.1:8000/api/users/1/\`



Example body:



\`\`\` json

{

&#x20; "phone": "155555556"

}

\`\`\`

patch is for partial change&#x20;





\#Update a user with PUT



\`PUT http\://127.0.0.1:8000/api/users/1/\`



PUT is intended for a full update. Send all fields required by your

serializer. If the serializer marks \`password\` as required for PUT, it

may reject the request when password is omitted. Ensure password updates

are handled securely and hashed rather than stored as plain text.



**# Soft-delete a user**



\`DELETE http\://127.0.0.1:8000/api/users/1/\`



The project should change the user's status to \`Inactive\` instead of

deleting the database row. The API's active-only list should then omit

that user.



**# Login and JWT usage**



\`POST http\://127.0.0.1:8000/api/auth/login/\`



by sending email and password returns accdss token&#x20;



For endpoints configured to require authentication, use the \*\*access

token\*\* in Postman:



1\.  Open the request's **\*\*Authorization\*\*** tab.

2\.  Select **\*\*Bearer Token\*\***.

3\.  Paste the access token returned by login.

4\.  Send the request.



The header format is:



\`\`\` text

Authorization: Bearer \<access_token>

\`\`\`



Do not send the refresh token as the normal API access token. JWT

authentication settings alone do not make every endpoint protected;

permissions on each view determine whether authentication is required.



**# OTP and password reset flow**



Use the request fields defined in your current serializers. The usual

flow is:



1\.  \`/api/auth/send-otp/\` to request an email OTP.

2\.  \`/api/auth/verify-otp/\` with the email and OTP fields expected

&#x20;   by the serializer.

3\.  For a forgotten password, call \`/api/auth/forgot-password/\`.

4\.  Use the reset OTP with \`/api/auth/reset-password/\` and the new

&#x20;   password field expected by your serializer.



it uses 5 minutes OTP expiry sent by email.expired incorect and already used OTP should be rejected



**# Testing with Postman**



1\.  Start the Django development server.

2\.  Open your saved Postman collection.

3\.  Test user creation and confirm the welcome email is received.

4\.  Test list, retrieve, PUT, PATCH, and soft-delete operations.

5\.  Test login and save the access token from the response.

6\.  Test OTP verification and password reset, including invalid or

&#x20;   expired OTP cases.

7\.  If a protected endpoint is configured, test it with a valid access

&#x20;   token and without a token.



Expected status codes depend on the view implementation. Common results

include \`200 OK\` for successful reads/updates, \`201 Created\` for

successful creation, \`400 Bad Request\` for validation errors,

\`401 Unauthorized\` for missing/invalid authentication on protected

endpoints, and \`404 Not Found\` for a user that cannot be found.

**# Client Management API**

The project also includes a `Client` model in the `users` application. It stores client contact information and tracks which authenticated user created the record and who last modified it.

## Client model fields

| Field | Description |
|---|---|
| `first_name` | Client's first name (maximum 100 characters) |
| `last_name` | Client's last name (maximum 100 characters) |
| `address` | Client's address |
| `country` | Client's country (maximum 100 characters) |
| `contact_number` | Client's contact number stored as text |
| `email` | Client's email address; must be unique |
| `status` | `Active` or `Inactive`; defaults to `Active` |
| `created_at` | Automatically set when the client is created |
| `created_by` | Foreign key to the user who created the client |
| `modified_at` | Automatically updated when the client model is saved |
| `modified_by` | Foreign key to the user who last modified the client |

The `created_by` and `modified_by` fields use `ForeignKey` relationships to the `User` model. `on_delete=models.PROTECT` prevents a referenced user from being deleted while related client records exist. The `related_name` values allow reverse lookups such as `user.created_clients.all()` and `user.modified_clients.all()`.

## Client API endpoints

These endpoints use the routes configured in the project. The examples below assume they are included at `/api/clients/` and require JWT authentication, as configured in the client views.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/clients/` | List active clients with pagination |
| `POST` | `/api/clients/` | Create a client |
| `GET` | `/api/clients/<id>/` | Retrieve one active client |
| `PUT` | `/api/clients/<id>/` | Fully update a client |
| `PATCH` | `/api/clients/<id>/` | Partially update a client |
| `DELETE` | `/api/clients/<id>/` | Soft-delete a client by setting its status to `Inactive` |

Replace `<id>` with the client's database ID. Confirm the exact URL prefix in `users/urls.py` and `user_model/urls.py` if your route configuration differs.

## Create a client in Postman

Send a `POST` request to:

```text
http://127.0.0.1:8000/api/clients/
```

In Postman, select **Authorization → Bearer Token** and provide a valid JWT access token. Select **Body → raw → JSON** and use a request body such as:

```json
{
  "first_name": "Rahul",
  "last_name": "Sharma",
  "address": "123 Example Street",
  "country": "India",
  "contact_number": "+919876543210",
  "email": "rahul.sharma@example.com",
  "status": "Active"
}
```

Use an email address that has not already been registered for another client. The example values are illustrative only. Do not send `created_at`, `created_by`, `modified_at`, or `modified_by` in the request body; these fields are read-only in the serializer. The API view sets the creator and modifier from the authenticated user.

## Update a client

**Partial update (`PATCH`)** — send only the fields you want to change:

```http
PATCH http://127.0.0.1:8000/api/clients/1/
```

Example JSON body:

```json
{
  "contact_number": "+919876505555"
}
```

**Full update (`PUT`)** — send all fields required by the serializer.

## Pagination and soft deletion

- `GET /api/clients/` returns active clients using page-number pagination. For example, `?page=2` requests the second page. The configured page size depends on the project's REST framework settings.
- `DELETE /api/clients/<id>/` sets the client's status to `Inactive` rather than permanently removing the database row.
- The list and detail views retrieve active clients only, so a deactivated client will no longer appear in the active list and its detail endpoint will return `404 Not Found`.
- The API records the authenticated user in `created_by` on creation and updates `modified_by` when a client is edited or deactivated.

Add client testing to your Postman checks: create a client, list clients, retrieve one client, test `PUT` and `PATCH`, and verify that `DELETE` deactivates rather than physically removes the record.
