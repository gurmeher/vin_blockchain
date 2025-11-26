# VIN Blockchain

A decentralized blockchain-based system for tracking Vehicle Identification Numbers (VINs), ownership transfers, and odometer readings. Uses a custom blockchain implementation with Proof of Work consensus.

## Features

- VIN registration with 17-character validation
- Ownership transfer between parties
- Odometer tracking with validation (mileage must increase)
- Block mining with Proof of Work consensus
- Complete VIN history queries
- RESTful API endpoints

## Technology Stack

- Python 3.10+
- Flask - Web framework
- Flask-CORS - CORS support
- Gunicorn - Production WSGI server
- Docker - Containerization

## Installation

### Local Development

```bash
git clone <repository-url>
cd carblockchain
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

API available at `http://localhost:3000`

### Docker

```bash
docker build -t vin-blockchain .
docker run -p 3000:3000 vin-blockchain
```

## API Documentation

Base URL: `http://localhost:3000`

### Endpoints

**GET /** - Health check
```json
{"message": "Flask API is running"}
```

**GET /chain?limit=5** - Get blockchain (limit defaults to 5)
```json
{
  "length": 10,
  "returned": 5,
  "chain": [...]
}
```

**GET /mine** - Mine a new block with pending transactions
```json
{
  "message": "Block mined successfully!",
  "index": 2,
  "transactions": [...],
  "nonce": 12345,
  "previous_hash": "..."
}
```

**POST /vin/register** - Register new vehicle
```json
Request: {"vin": "1HGBH41JXMN109186", "owner": "John Doe"}
Response: {"message": "VIN registration added to pending transactions", "will_be_added_to_block": 2}
```

**POST /vin/transfer** - Transfer ownership
```json
Request: {"vin": "1HGBH41JXMN109186", "from_owner": "John Doe", "to_owner": "Jane Smith"}
Response: {"message": "Ownership transfer added to pending transactions", "will_be_added_to_block": 2}
```

**POST /vin/odometer** - Update odometer reading
```json
Request: {"vin": "1HGBH41JXMN109186", "mileage": 50000}
Response: {"message": "Odometer update added to pending transactions", "will_be_added_to_block": 2}
```

**GET /vin/{vin}** - Get VIN history
```json
{
  "vin": "1HGBH41JXMN109186",
  "history": [...],
  "records_found": 5
}
```

## Blockchain Features

**Proof of Work**: Miners find a nonce such that `hash(previous_nonce + previous_hash + nonce)` starts with `0000`.

**Transaction Types**:
- `register_vehicle` - Initial vehicle registration
- `transfer_ownership` - Ownership transfer
- `odometer_update` - Odometer reading update

**Block Structure**: index, timestamp, transactions, nonce, previous_hash

## Deployment

**Heroku**:
```bash
heroku create your-app-name
git push heroku main
```

**Production**:
```bash
gunicorn app:app --bind 0.0.0.0:3000
```

## Project Structure

```
carblockchain/
├── app.py              # Flask application and API endpoints
├── blockchain.py       # Blockchain implementation
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── Procfile           # Heroku deployment configuration
└── README.md          # Project documentation
```

## Example Usage

```bash
# Register vehicle
curl -X POST http://localhost:3000/vin/register \
  -H "Content-Type: application/json" \
  -d '{"vin": "1HGBH41JXMN109186", "owner": "John Doe"}'

# Mine block
curl http://localhost:3000/mine

# Transfer ownership
curl -X POST http://localhost:3000/vin/transfer \
  -H "Content-Type: application/json" \
  -d '{"vin": "1HGBH41JXMN109186", "from_owner": "John Doe", "to_owner": "Jane Smith"}'

# Update odometer
curl -X POST http://localhost:3000/vin/odometer \
  -H "Content-Type: application/json" \
  -d '{"vin": "1HGBH41JXMN109186", "mileage": 50000}'

# View history
curl http://localhost:3000/vin/1HGBH41JXMN109186
```

## Note

This is an educational project demonstrating blockchain concepts. For production use, additional security measures, consensus mechanisms, and validation would be required.
