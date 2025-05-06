# WasteLess

## Project Title

**WasteLess**: A food-waste prevention app that tracks items in shared fridges, calculates spoil dates, and sends notifications when items are about to go bad or have spoiled.

## Description

WasteLess allows multiple users to share one or more fridges. It automatically reads product expiry dates via QR-code scans, adjusts spoilage timelines once items are opened, and notifies users to reduce food waste.

The project consists of:

1. **Database Schema (Question 1)**: A normalized MySQL schema with tables for users, fridges, products, QR codes, fridge items, and notifications. Spoil dates are computed dynamically based on opening dates.
2. **CRUD API (Question 2)**: A FastAPI backend connected to the MySQL database, providing full Create, Read, Update, Delete endpoints for Users, Fridges, Fridge-Sharing, Fridge Items, and Notifications.

## Getting Started

### Prerequisites

* MySQL server
* Python&#x20;

### Database Setup

1. Import the SQL schema:

   ```bash
   mysql -u <username> -p < wasteless_schema.sql
   ```
2. (Optional) Load sample data:

   ```bash
   mysql -u <username> -p wasteless < sample_data.sql
   ```

### Backend Setup (FastAPI)

1. Navigate to the `wasteless-api` directory:

   ```bash
   cd wasteless-api
   ```
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/Scripts/activate  # or venv/bin/activate on Unix
   ```
3. Configure database credentials in `app/db.py`.
4. Run the server:

   ```bash
   uvicorn app.main:app --reload
   ```
5. Swagger UI available at `http://127.0.0.1:8000/docs`

## Repository Structure

```
root/   
|-- images/
      |---   
├── wasteless.sql         # Question 1: Well-commented SQL schema and Sample data inserts
├── wasteless-api/        # Question 2: Backend
│   ├── app/
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── main.py


```

##

## Schema Diagram 
![WasteLess](images\WastLessio.jpg)