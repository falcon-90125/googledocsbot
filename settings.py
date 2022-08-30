import os
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS = {
  "type": "service_account",
  "project_id": "my-first-project-360914",
  "private_key_id": os.getenv('PRIVATE_KEY_ID', ''),
  "private_key": os.getenv('PRIVATE_KEY', ''),
  "client_email": "google-sheets-api@my-first-project-360914.iam.gserviceaccount.com",
  "client_id": os.getenv('CLIENT_ID', ''),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-api%40my-first-project-360914.iam.gserviceaccount.com"
}
