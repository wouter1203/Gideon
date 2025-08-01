import sqlite3

DB_PATH = "state.db"

def initialize_db():
    """Initialize the database and create the state table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def set_state(key, value):
    """Set a key-value pair in the state table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO state (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()

def get_state(key):
    """Get the value of a key from the state table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM state WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_states():
    """Retrieve all key-value pairs from the state table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM state")
    results = cursor.fetchall()
    conn.close()
    return results

def clear_state():
    """Clear all state entries."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM state")
    conn.commit()
    conn.close()

# CLI functionality
if __name__ == "__main__":
    initialize_db()
    print("Welcome to the State Manager CLI!")
    print("Available commands:")
    print("1. View all states")
    print("2. Get a specific state")
    print("3. Set a state")
    print("4. Clear all states")
    print("5. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            if choice == "1":
                # View all states
                states = get_all_states()
                if states:
                    print("\nCurrent states:")
                    for key, value in states:
                        print(f"  {key}: {value}")
                else:
                    print("\nNo states found.")
            elif choice == "2":
                # Get a specific state
                key = input("Enter the key to retrieve: ").strip()
                value = get_state(key)
                if value:
                    print(f"\nValue for '{key}': {value}")
                else:
                    print(f"\nNo value found for key '{key}'.")
            elif choice == "3":
                # Set a state
                key = input("Enter the key to set: ").strip()
                value = input("Enter the value: ").strip()
                set_state(key, value)
                print(f"\nState '{key}' set to '{value}'.")
            elif choice == "4":
                # Clear all states
                confirm = input("Are you sure you want to clear all states? (yes/no): ").strip().lower()
                if confirm == "yes":
                    clear_state()
                    print("\nAll states cleared.")
                else:
                    print("\nOperation canceled.")
            elif choice == "5":
                # Exit
                print("\nExiting State Manager CLI. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 5.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")