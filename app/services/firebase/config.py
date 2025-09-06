import firebase_admin
from firebase_admin import credentials, firestore
import os
from typing import Optional, Any
from dotenv import load_dotenv
load_dotenv()

class FirebaseConfig:
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseConfig, cls).__new__(cls)
        return cls._instance
    
    def initialize_firebase(self) -> Any:
        """
        Initialize Firebase Admin SDK and return Firestore client.
        
        Returns:
            Any: Firestore database client
        """
        if self._db is not None:
            return self._db
        
        try:
            # Method 1: Using service account key file (recommended for production)
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
            
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print("Firebase initialized with service account key file")
            
            # Method 2: Using environment variables (alternative)
            elif os.getenv('FIREBASE_PROJECT_ID'):
                # This method uses Application Default Credentials or environment variables
                project_id = os.getenv('FIREBASE_PROJECT_ID')
                
                # If you have the service account key as environment variables
                service_account_info = {
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL')}"
                }
                
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id,
                })
                print("Firebase initialized with environment variables")
            
            # Method 3: Development/testing mode (not recommended for production)
            else:
                print("Warning: No Firebase credentials found. Using default credentials (not recommended for production)")
                firebase_admin.initialize_app()
            
            # Initialize Firestore client
            self._db = firestore.client()
            return self._db
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise e
    
    def get_db(self) -> Optional[Any]:
        """
        Get the Firestore database client.
        
        Returns:
            Any or None: Firestore database client
        """
        if self._db is None:
            return self.initialize_firebase()
        return self._db

# Global Firebase instance
firebase_config = FirebaseConfig()

def get_firebase_db() -> Any:
    """
    Get Firebase Firestore database instance.
    
    Returns:
        Any: Firestore database client
    """
    return firebase_config.get_db()
