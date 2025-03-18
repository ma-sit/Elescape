import os
import json
import time
from typing import Dict, List, Optional, Any

# Constants
DATA_DIR = "data"
USERS_DIR = os.path.join(DATA_DIR, "users")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")

def initialize_system():
    """Initialize the user account system by creating necessary directories."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(USERS_DIR, exist_ok=True)
    
    # Create accounts file if it doesn't exist
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump({"users": {}}, f)

def username_exists(username: str) -> bool:
    """Check if a username already exists in the system."""
    if not os.path.exists(ACCOUNTS_FILE):
        return False
    
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)
    
    return username in accounts.get("users", {})

def create_user(username: str) -> bool:
    """
    Create a new user account with the given username.
    Returns True if successful, False if the username already exists.
    """
    if username_exists(username):
        return False
    
    # Create user directory
    user_dir = os.path.join(USERS_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    
    # Add to accounts file
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)
    
    accounts.setdefault("users", {})
    accounts["users"][username] = {
        "created_at": time.time(),
        "last_login": time.time()
    }
    
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)
    
    # Create initial progression file
    progression = {"niveaux_debloques": [1], "elements_decouverts": []}
    progression_file = os.path.join(user_dir, "progression.json")
    
    with open(progression_file, "w") as f:
        json.dump(progression, f)
    
    return True

def get_all_users() -> List[str]:
    """Return a list of all registered usernames."""
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)
    
    return list(accounts.get("users", {}).keys())

def get_user_data_path(username: str) -> str:
    """Return the path to the user's data directory."""
    return os.path.join(USERS_DIR, username)

def get_progression_file_path(username: str) -> str:
    """Return the path to the user's progression file."""
    return os.path.join(get_user_data_path(username), "progression.json")

def load_progression(username: str) -> Dict[str, Any]:
    """Load the progression data for a specific user."""
    file_path = get_progression_file_path(username)
    
    if not os.path.exists(file_path):
        # Create default progression if file doesn't exist
        progression = {"niveaux_debloques": [1], "elements_decouverts": []}
        save_progression(username, progression)
        return progression
    
    with open(file_path, "r") as f:
        return json.load(f)

def save_progression(username: str, progression: Dict[str, Any]) -> bool:
    """Save the progression data for a specific user."""
    file_path = get_progression_file_path(username)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        with open(file_path, "w") as f:
            json.dump(progression, f)
        return True
    except Exception as e:
        print(f"Error saving progression for user {username}: {e}")
        return False

def set_current_user(username: str) -> bool:
    """Set the current active user and update their last login time."""
    if not username_exists(username):
        return False
    
    # Update last login time
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)
    
    accounts["users"][username]["last_login"] = time.time()
    accounts["current_user"] = username
    
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)
    
    return True

def get_current_user() -> Optional[str]:
    """Get the current active user's username, or None if no user is set."""
    if not os.path.exists(ACCOUNTS_FILE):
        return None
    
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)
    
    return accounts.get("current_user")