import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import copy
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
MONGO_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('MONGO_DATABASE')
COLLECTION_NAME = "alerts"

def get_mongo_client():
    """Return a MongoDB client using the connection string."""
    return MongoClient(MONGO_URI)

def get_mongo_db():
    """Return the MongoDB database instance."""
    return get_mongo_client()[DATABASE_NAME]

def get_collections():
    """Get MongoDB collections."""
    db = get_mongo_db()
    return {
        'alerts': db['alerts'],
        'transactions': db['transactions'],
        'feedback': db['user_feedback']
    }

def get_all_alerts_with_transactions(limit=3, skip=0):
    """
    Fetch alerts with their associated transactions, excluding embeddings.
    Implements pagination with limit and skip.
    """
    collections = get_collections()
    
    # Fetch alerts with pagination (skip and limit)
    alerts = list(collections['alerts'].find({}, {"embedding": 0}).skip(skip).limit(limit))
    
    if not alerts:
        return []

    # Collect all transaction IDs
    all_transaction_ids = []
    for alert in alerts:
        transaction_ids = alert.get('transaction_ids', [])
        all_transaction_ids.extend(
            [ObjectId(tid) if isinstance(tid, str) else tid for tid in transaction_ids]
        )

    # Fetch only required transactions
    transaction_map = {}
    if all_transaction_ids:
        transactions = list(
            collections['transactions'].find(
                {"_id": {"$in": all_transaction_ids}},
                {"embedding": 0}
            )
        )
        transaction_map = {str(t['_id']): t for t in transactions}

    # Structure the response
    cleaned_alerts = []
    for alert in alerts:
        cleaned_alert = {
            '_id': str(alert['_id']),
            'alert_message': alert.get('alert_message', ''),
            'timestamp': alert.get('timestamp'),
            'sid': alert.get('sid', ''),
            'code': alert.get('code', ''),
            'transactions': []
        }

        # Attach only necessary transactions
        transaction_ids = alert.get('transaction_ids', [])
        for tid in transaction_ids:
            tid_str = str(tid)
            if tid_str in transaction_map:
                transaction = transaction_map[tid_str]
                cleaned_alert['transactions'].append({
                    'id': tid_str,
                    'system_name': transaction.get('system_name', ''),
                    'growth': parse_growth(transaction.get('growth', 0)),
                    'file_path': transaction.get('file_path', ''),
                    'timestamp': transaction.get('timestamp')
                })

        cleaned_alerts.append(cleaned_alert)

    return cleaned_alerts

def get_alert_with_transactions(alert_id):
    """
    Fetch a specific alert and its associated transactions.
    """
    collections = get_collections()
    
    try:
        alert = collections['alerts'].find_one(
            {"_id": ObjectId(alert_id)},
            {"embedding": 0}
        )
        
        if not alert:
            return None

        # Fetch associated transactions
        transaction_ids = alert.get('transaction_ids', [])
        transactions = []
        
        if transaction_ids:
            transactions = list(collections['transactions'].find(
                {"_id": {"$in": [ObjectId(tid) if isinstance(tid, str) else tid 
                                for tid in transaction_ids]}},
                {"embedding": 0}
            ))

        # Clean and structure the response
        cleaned_alert = {
            '_id': str(alert['_id']),
            'alert_message': alert.get('alert_message', ''),
            'timestamp': alert.get('timestamp'),
            'sid': alert.get('sid', ''),
            'code': alert.get('code', ''),
            'transactions': []
        }

        # Add cleaned transactions
        for transaction in transactions:
            cleaned_transaction = {
                'id': str(transaction['_id']),
                'system_name': transaction.get('system_name', ''),
                'growth': parse_growth(transaction.get('growth', 0)),
                'file_path': transaction.get('file_path', ''),
                'timestamp': transaction.get('timestamp')
            }
            cleaned_alert['transactions'].append(cleaned_transaction)

        return cleaned_alert
    except Exception as e:
        print(f"Error retrieving alert: {str(e)}")
        return None

def submit_feedback(feedback_data):
    """
    Submit feedback for an alert.
    """
    collections = get_collections()
    
    try:
        feedback_entry = {
            'alertId': ObjectId(feedback_data['alert_id']),
            'alertMessage': feedback_data.get('alert_message', ''),
            'rating': feedback_data.get('rating', 0),
            'comment': feedback_data.get('comment', ''),
            'timestamp': datetime.utcnow()
        }
        
        result = collections['feedback'].insert_one(feedback_entry)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error submitting feedback: {str(e)}")
        return None

def parse_growth(growth):
    """Parse growth value from string or number."""
    if isinstance(growth, str):
        try:
            return float(growth.replace('%', '').strip())
        except (ValueError, AttributeError):
            return 0.0
    return float(growth) if growth else 0.0
from pymongo import MongoClient

def save_alert_to_collection(alert_data, collection_name):
    client = MongoClient()  # Adjust if you have a different MongoDB connection setup
    db = client['your_database']  # Replace with your actual database name
    collection = db[collection_name]
    collection.insert_one(alert_data) 