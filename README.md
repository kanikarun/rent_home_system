# Rent Home System

[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/kanikarun/rent_home_system)

A comprehensive rental property management system built with Flask. This web application provides a user-friendly interface for managing properties, tenants, contracts, payments, and maintenance requests.

## Features

*   **Property Management**: Add, edit, and delete properties and their associated rooms. Categorize properties by type (e.g., Apartment, House).
*   **Tenant Management**: Maintain a database of tenants, including their personal information, contact details, and ID documents.
*   **Contract Management**: Create and manage rental contracts, linking tenants to specific rooms with defined start/end dates, deposit amounts, and monthly rent. The system prevents booking conflicts.
*   **Payment Tracking**: Record and track monthly rent payments for each contract. The system calculates total paid and remaining balances.
*   **Maintenance Requests**: Log, update, and track maintenance requests submitted by tenants, including description, status, and cost.
*   **User & Role Management**: Manage system users with different roles (Administrator, Manager, Staff).
*   **Dynamic UI**: A responsive frontend built with vanilla JavaScript that interacts with the Flask backend via a RESTful API.

## Technology Stack

*   **Backend**: Python, Flask, Flask-SQLAlchemy
*   **Database**: SQLite
*   **Migrations**: Flask-Migrate, Alembic
*   **Frontend**: HTML, CSS, Vanilla JavaScript

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.x
*   pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/kanikarun/rent_home_system.git
    cd rent_home_system
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    py -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```sh
    pip install Flask Flask-SQLAlchemy Flask-Migrate
    ```

4.  **Set up the database:**
    The project uses Flask-Migrate to manage database schema changes. Run the following command to apply all migrations and create the `instance/rent_home.db` database file.
    ```sh
    flask db upgrade
    ```

5.  **Run the application:**
    ```sh
    python app.py
    ```

6.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

    *   **Username**: `admin`
    *   **Password**: `123`

## Project Structure

The repository is organized as follows:

```
rent_home_system/
├── app.py                  # Main Flask application file and core routes
├── instance/
│   └── rent_home.db        # SQLite database file
├── migrations/             # Alembic database migration scripts
├── models/                 # SQLAlchemy database models
├── routes/                 # API endpoint route definitions
├── static/                 # Frontend assets (CSS, JS, images)
└── templates/              # Jinja2 HTML templates
```

## API Endpoints

The application exposes a RESTful API for managing resources.

### Properties
- `GET /api/properties`: Get all properties.
- `GET /api/properties/<id>`: Get a single property by ID.
- `POST /api/properties/create`: Create a new property with rooms.
- `PUT /api/properties/update/<id>`: Update a property and its rooms.
- `DELETE /api/properties/delete`: Delete a property.
- `GET /api/owners`: Get all property owners.
- `POST /api/owners/create`: Create a new owner.
- `GET /api/properties/types`: Get all property types.
- `POST /api/properties/type/create`: Create a new property type.

### Rooms
- `GET /api/rooms`: Get all rooms.
- `GET /api/properties/<id>/rooms`: Get all rooms for a specific property.
- `DELETE /api/rooms/<id>`: Delete a room.

### Tenants
- `GET /api/tenants`: Get all tenants.
- `GET /api/tenants/<id>`: Get a single tenant by ID.
- `POST /api/tenants/create`: Create a new tenant.
- `PUT /api/tenants/update/<id>`: Update a tenant's information.
- `DELETE /api/tenants/delete`: Delete a tenant.

### Contracts
- `GET /api/contracts`: Get all contracts with tenant and property details.
- `POST /api/contracts`: Create a new contract.
- `PUT /api/contracts/<id>`: Update an existing contract.
- `DELETE /api/contracts/<id>`: Delete a contract.

### Payments
- `GET /api/payments`: Get all payments.
- `POST /api/payments/create`: Add a new payment record.
- `PUT /api/payments/<id>`: Update a payment record.
- `DELETE /api/payments/<id>`: Delete a payment record.

### Maintenance
- `GET /api/maintenance`: Get all maintenance requests.
- `GET /api/maintenance/<id>`: Get a specific request.
- `POST /api/maintenance/create`: Create a new maintenance request.
- `PUT /api/maintenance/update/<id>`: Update a maintenance request.
- `DELETE /api/maintenance/delete/<id>`: Delete a maintenance request.

### Users
- `GET /api/users`: Get all users.
- `GET /api/users/<id>`: Get a single user.
- `POST /api/users/create`: Create a new user.
- `PUT /api/users/update/<id>`: Update a user's details.
- `DELETE /api/users/delete`: Delete a user.

## Database Schema

The database consists of the following tables:

*   **Users**: Stores user accounts and their roles.
*   **Owners**: Stores information about property owners.
*   **PropertiesType**: Defines types of properties (e.g., 'Apartment', 'House').
*   **Properties**: Contains details about each rental property, linked to an owner and a type.
*   **Rooms**: Represents individual rooms within a property, including rent price and availability status.
*   **Tenants**: Stores personal and contact information for each tenant.
*   **Contracts**: Links a `Tenant` to a `Room` for a specific duration, defining the rental agreement.
*   **Payments**: Records all payment transactions related to a contract.
*   **MaintenanceRequests**: Tracks maintenance issues reported for a room by a tenant.
