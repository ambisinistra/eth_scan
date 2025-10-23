# Ethereum Transaction Viewer

A Flask application for viewing Ethereum transactions with pagination.

## Project Structure

```
project/
├── app_input.py              # Main application file
├── result.txt          # JSON file with transactions
├── templates/
│   └── *.html      # HTML templates
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
└── README.md           # Documentation
```

## Running Without Docker

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Start the application:
```bash
python app_input.py
```

### 3. Open in your browser:
```
http://localhost:5000
http://127.0.0.1:5000
```

## Running With Docker

### 1. Build the image:
```bash
docker build -t eth-viewer .
```

### 2. Run the container:
```bash
docker run -p 5000:5000 eth-viewer
```

### 3. Open in your browser:
```
http://localhost:5000
http://127.0.0.1:5000
```

## How the Application Works

### Main Components

This application sends a request to the Etherscan API to retrieve Ethereum transactions and displays the results in a web browser using Flask.  
It supports pagination (20 transactions per page) and shows key transaction details such as block number, sender, receiver, value in ETH, and status.

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

1. Add PostgreSQL for data storage    
2. Implement filters (date, transaction direction)    
3. Add ERC-20 token support
