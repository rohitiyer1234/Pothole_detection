import os
from dotenv import load_dotenv
from app import app

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Get port from environment variable or use default 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Run the application
    app.run(host="0.0.0.0", port=port, debug=True)