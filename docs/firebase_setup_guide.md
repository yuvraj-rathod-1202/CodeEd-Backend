# Firebase Setup Guide

## Prerequisites
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database in your Firebase project

## Step 1: Create a Service Account

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file (this is your service account key)
4. Rename it to something like `firebase-service-account.json`

## Step 2: Setup Firebase Authentication

Choose ONE of the following methods:

### Method 1: Service Account Key File (Recommended)

1. Place the service account JSON file in a secure location (e.g., `config/` folder)
2. Add to your `.env` file:
   ```
   FIREBASE_SERVICE_ACCOUNT_PATH=path/to/your/firebase-service-account.json
   ```

### Method 2: Environment Variables

Extract the following values from your service account JSON file and add them to `.env`:

```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
```

**Note**: Make sure to escape newlines in the private key as `\n`

## Step 3: Security Considerations

1. **Never commit** service account keys or `.env` files to version control
2. Add these to your `.gitignore`:
   ```
   .env
   .env.local
   .env.production
   firebase-service-account.json
   config/firebase-service-account.json
   ```

3. For production, use secure secret management services

## Step 4: Firestore Database Rules

Set up your Firestore security rules. Example rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access to authenticated users
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
    
    // Or more specific rules
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /quizzes/{quizId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

## Step 5: Testing Your Setup

Create a test script to verify Firebase connection:

```python
from app.services.firebase.config import get_firebase_db

def test_firebase_connection():
    try:
        db = get_firebase_db()
        print("✅ Firebase connected successfully!")
        
        # Test writing data
        test_ref = db.collection('test').document('connection_test')
        test_ref.set({
            'message': 'Hello Firebase!',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        print("✅ Test document created successfully!")
        
        # Test reading data
        doc = test_ref.get()
        if doc.exists:
            print(f"✅ Test document read: {doc.to_dict()}")
        
        # Clean up test document
        test_ref.delete()
        print("✅ Test document deleted successfully!")
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")

if __name__ == "__main__":
    test_firebase_connection()
```

## Step 6: Usage in Your Application

The Firebase database is now initialized and can be used throughout your application:

```python
from app.services.firebase.config import get_firebase_db

# Get database instance
db = get_firebase_db()

# Use Firestore operations
users_ref = db.collection('users')
docs = users_ref.stream()

for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')
```

## Troubleshooting

### Common Issues:

1. **"Default app already exists"**: This means Firebase is already initialized. The singleton pattern in our config prevents this.

2. **"Invalid service account"**: Check that your service account JSON is valid and the paths are correct.

3. **"Permission denied"**: Ensure your Firestore rules allow the operations you're trying to perform.

4. **"Project not found"**: Verify your project ID is correct in the configuration.

### Debug Mode:

Set the following environment variable for more detailed logs:
```bash
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-file.json
```

## Collection Structure Recommendations

For your application, consider this Firestore structure:

```
/users/{userId}
  - country: string
  - goal: string
  - experience: string
  - interests: array
  - education: string
  - created_at: timestamp

/quizzes/{quizId}
  - userId: string
  - questions: array
  - created_at: timestamp
  - score: number

/flowcharts/{flowchartId}
  - userId: string
  - content: string
  - created_at: timestamp
```

This setup ensures your Firebase is properly configured and secure!
