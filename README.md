# Budget Tracker

A simple and intuitive web application designed to help you manage your personal finances with ease. Built with Python and the Flask framework, this budget tracker provides a clear overview of your income and expenses.

## Key Features

- **User Authentication**: Secure sign-up and login functionality to keep your financial data private.
- **Transaction Management**: Easily add new transactions, classifying them as either income or expense.
- **Financial Dashboard**: A centralized dashboard that displays:
  - Total income
  - Total expenses
  - Current account balance
  - A detailed list of all your past transactions.
- **Data Reset**: A feature to completely reset your transaction data and start over.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: Flask-SQLAlchemy for ORM
- **Forms**: Flask-WTF for secure web forms
- **Templating**: Jinja2
- **Deployment**: Gunicorn

## Deployment

This application is deployed on [Railway](https://railway.app/).

## Local Development

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd budget-tracker
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```sh
    python run.py
    ```

The application will be running at `http://127.0.0.1:5000`.