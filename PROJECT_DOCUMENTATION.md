# Megastation Project Documentation

## 1. Project Overview

Megastation is a comprehensive e-commerce and inventory management system. It features a customer-facing online store and a powerful backend for staff to manage products, inventory, orders, purchases, and view analytics. The system is designed with role-based access control to cater to different user types, from customers to superusers.

## 2. Technology Stack

*   **Backend**: Django, Django REST Framework
*   **Frontend**: Vue.js (v3), Vue Router, Pinia
*   **Database**: (Not specified, likely PostgreSQL or SQLite for development)
*   **Authentication**: JWT (JSON Web Tokens) via `rest_framework_simplejwt`

## 3. Project Structure

The project is a monorepo containing both the Django backend and the Vue.js frontend.

-   `megastation/`: Main Django project directory.
-   `{app_name}/`: Individual Django applications (`users`, `store`, `orders`, etc.).
-   `frontend/`: The Vue.js frontend application.
-   `manage.py`: Django's command-line utility.
-   `requirements.txt`: Python dependencies.
-   `package.json`: Node.js dependencies.

---

## 4. Backend (Django)

The backend is built as a REST API using Django REST Framework.

### 4.1. `users` App

*   **Purpose**: Manages users, authentication, and permissions.
*   **Models**:
    *   `CustomUser(AbstractUser)`: Extends the default Django user with a `role` field.
        *   **Roles**: `superuser`, `admin`, `store_admin`, `seller`, `customer`.
        *   **`sales_point`**: Links staff members to a specific point of sale.
*   **API Endpoints (`/api/users/`)**:
    *   `/login/`, `/logout/`, `/register/`: User authentication.
    *   `/token/refresh/`: JWT token refreshing.
    *   `/me/`: Get current user's data.
    *   `/`: List users (Admin/Superuser).
    *   `/<id>/`: Get user details (Admin/Superuser).
    *   `/customers/`: List users with the 'customer' role.

### 4.2. `store` App

*   **Purpose**: Manages products and categories.
*   **Models**:
    *   `Category`: `name`, `min_stock`.
    *   `Product`: `name`, `description`, `price`, `barcode`, `image`, `category`.
*   **API Endpoints (`/api/store/`)**:
    *   `/products/`: List and create products.
    *   `/products/<id>/`: Retrieve, update, delete a specific product.
    *   `/categories/`: List and create categories.
    *   `/categories/<id>/`: Retrieve, update, delete a specific category.

### 4.3. `cart` App

*   **Purpose**: Manages the shopping cart functionality.
*   **Models**:
    *   `CartItem`: Links a `user`, a `product`, and `quantity`. `unique_together` on user and product.
*   **API Endpoints (`/api/`)**:
    *   `/`: List items in the current user's cart.
    *   `/<id>/`: Update or delete a specific item from the cart.

### 4.4. `orders` App

*   **Purpose**: Manages customer orders and payments.
*   **Models**:
    *   `Order`: `user`, `status` (`pendiente`, `en_proceso`, `enviado`, `cancelado`), `total_price`, `payment_method`.
    *   `OrderItem`: Links an `order` to a `product`, `quantity`, and `sales_point` it was sold from.
*   **API Endpoints (`/api/orders/`)**:
    *   `/`: List orders for the current user.
    *   `/create/`: Create a new order from the cart.
    *   `/<id>/`: Get details of a specific order.
    *   `/<id>/cancel/`: Cancel an order.
    *   `/staff/`: List orders for staff members.
    *   `/create-payment/`: Endpoint for initiating a payment (e.g., MercadoPago).
    *   `/webhook/`: Webhook for receiving payment status updates from MercadoPago.

### 4.5. `inventory` App

*   **Purpose**: Manages stock levels, points of sale, and stock movements.
*   **Models**:
    *   `SalesPoint`: A physical or virtual location for stock (`name`, `administrators`, `sellers`).
    *   `Stock`: Represents the quantity of a `product` at a specific `sales_point`. Includes `quantity`, `reserved_quantity`, and `low_stock_threshold`.
    *   `StockMovement`: A log of every change in stock (`product`, `sales_point`, `change`, `reason`).
*   **API Endpoints (`/api/inventory/`)**:
    *   `/stock/`: List stock levels.
    *   `/sales-points/`: List points of sale.
    *   `/stock-movements/`: List and create stock movements.

### 4.6. `purchases` App

*   **Purpose**: Manages purchasing from suppliers, including invoices and returns.
*   **Models**:
    *   `Invoice`: Represents a purchase invoice from a `supplier`. Linked to a `sales_point`. Has `status` (`pendiente`, `procesada`, `anulada`). Contains logic to automatically update stock (`update_stock`, `revert_stock`).
    *   `InvoiceItem`: An item within an invoice (`product`, `quantity`, `cost_per_item`).
    *   `InvoiceReturn`: Represents a return of goods to a supplier. Contains logic to validate the return and update stock.
*   **API Endpoints (`/api/purchases/`)**:
    *   `/invoices/`: List and create invoices.
    *   `/invoices/<id>/`: Retrieve, update, delete an invoice.
    *   `/invoices/<id>/status/`: Update invoice status.
    *   `/invoices/returns/`: List and create invoice returns.

### 4.7. `analytics` App

*   **Purpose**: Provides aggregated data for business intelligence.
*   **API Endpoints (`/api/analytics/`)**:
    *   `/`: A single, powerful endpoint (`AnalyticsView`) that returns a comprehensive set of statistics based on query parameters (date range, sales point).
    *   **Metrics**: Includes stats on products (low stock), orders (revenue, top sellers), and purchases (costs, top buys).

---

## 5. Frontend (Vue.js)

The frontend is a Single Page Application (SPA) built with Vue.js.

*   **Routing (`frontend/src/router/index.js`)**: Uses `vue-router` for navigation. Implements a navigation guard (`beforeEach`) to handle authentication and role-based authorization for protected routes.
*   **State Management**: Uses Pinia (`useUserStore`) for managing global user state, including authentication status and user details.
*   **Views (`frontend/src/views/`)**:
    *   **Public**: `Home`, `Catalog`, `Product`, `Cart`, `Login`.
    *   **Authenticated**: `Profile`, `Checkout`, `Orders`.
    *   **Staff-Only**:
        *   `Dashboard`: Analytics view (`superuser`, `admin`, `store_admin`).
        *   `StaffOrders`: Order management for staff.
        *   `Invoices`, `InvoiceCreate`, `InvoiceDetail`: Purchase management.
        *   `StockLevels`: Inventory overview.
        *   `UserList`: User management (`superuser`, `admin`).

---

## 6. Key Business Logic

*   **Role-Based Access Control (RBAC)**: Both backend (DRF permissions) and frontend (router guards) enforce strict rules based on user roles, ensuring users only see and do what they are permitted.
*   **Transactional Stock Management**: All operations that affect stock quantities (processing invoices, creating returns, cancelling orders) are wrapped in database transactions to ensure data integrity. Every change is logged in the `StockMovement` model for traceability.
*   **Integrated Sales and Inventory**: When an order is placed, the system knows which `SalesPoint` the stock is drawn from. When a purchase invoice is processed, stock is added to the specified `SalesPoint`. This provides a clear link between sales, purchases, and real-time inventory levels.
