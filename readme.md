# Ethereum Transaction Viewer

A Flask application for viewing Ethereum transactions with pagination and PostgreSQL database storage.

## Project Structure

```
project/
├── app_input.py              # Main application file
├── result.txt                # JSON file with transactions
├── templates/
│   └── *.html               # HTML templates
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── README.md                # Documentation
```

## Running Without Docker

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL database:
Make sure PostgreSQL is running and create a database named `lets_goto_it`.

### 3. Set environment variable:
```bash
export DATABASE_URL=postgresql://usr:pass@localhost:5432/lets_goto_it
```

### 4. Start the application:
```bash
python app_input.py
```

### 5. Open in your browser:
```
http://localhost:5000
http://127.0.0.1:5000
```

## Running With Docker Compose (Recommended)

### 1. Build and start all services:
```bash
docker-compose up --build
```

Or run in detached mode:
```bash
docker-compose up -d --build
```

### 2. Stop the services:
```bash
docker-compose down
```

### 3. Stop and remove volumes (database data):
```bash
docker-compose down -v
```

### 4. Open in your browser:
```
http://localhost:5000
http://127.0.0.1:5000
```

## Docker Compose Services

The application uses two services:

- **psql** – PostgreSQL 15 database
  - Port: 5432
  - Database: `lets_goto_it`
  - User: `usr`
  - Password: `pass`
  - Data is stored in a named volume `postgres_data`

- **app** – Flask application
  - Port: 5000
  - Depends on PostgreSQL service
  - Connects to database using `DATABASE_URL`

## How the Application Works

### Main Components

This application sends a request to the Etherscan API to retrieve Ethereum transactions and displays the results in a web browser using Flask.  
It supports pagination (20 transactions per page) and shows key transaction details such as block number, sender, receiver, value in ETH, and status.

Transaction data is stored in a PostgreSQL database for persistence and efficient querying.

### Example URLs:
- First page: `http://localhost:5000/`

## Displayed Fields:

- **Block** – block number  
- **Timestamp** – date and time of the transaction  
- **Hash** – shortened transaction hash  
- **From** – shortened sender address  
- **To** – shortened receiver address  
- **Value (ETH)** – transaction amount in ETH  
- **Gas Used** – gas used for the transaction  
- **Status** – transaction status (Success/Failed)

## Next Steps for Full Implementation:

1. ~~Add PostgreSQL for data storage~~ ✓ Implemented
2. Implement filters (date, transaction direction)    
3. Add ERC-20 token support
4. Add transaction search functionality
5. Implement caching mechanism