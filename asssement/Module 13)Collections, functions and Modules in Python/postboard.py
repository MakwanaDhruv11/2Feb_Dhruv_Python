import datetime

# In-memory data storage
users = {}  # Format: {'username': 'password'}
posts = []  # Format: [{'author': 'username', 'title': 'post title', 'description': 'post desc', 'date': 'YYYY-MM-DD HH:MM:SS'}]

def get_non_empty_input(prompt):
    """Prompts the user for input until a non-empty string is provided."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Error: Input cannot be empty. Please try again.")

def register_user():
    """Handles the registration of a new user."""
    print("\n--- Register ---")
    while True:
        username = get_non_empty_input("Enter a new username: ")
        if username in users:
            print("Error: Username already exists. Please choose a different one.")
        else:
            break
            
    password = get_non_empty_input("Enter a password: ")
    users[username] = password
    print(f"Success! User '{username}' registered successfully.")

def login_user():
    """Handles user login and returns the username if successful."""
    print("\n--- Login ---")
    username = get_non_empty_input("Enter username: ")
    if username not in users:
        print("Error: Username not found.")
        return None
        
    password = get_non_empty_input("Enter password: ")
    if users[username] == password:
        print("Login successful!")
        return username
    else:
        print("Error: Incorrect password.")
        return None

def create_post(username):
    """Allows a logged-in user to create a new post."""
    print("\n--- Create a Post ---")
    title = get_non_empty_input("Enter post title: ")
    description = get_non_empty_input("Enter post description: ")
    
    # Auto-generate date
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    post = {
        'author': username,
        'title': title,
        'description': description,
        'date': current_time
    }
    posts.append(post)
    print("Success! Post created successfully.")

def format_post(post):
    """Helper function to print a post in a clean format."""
    print("-" * 40)
    print(f"Title:       {post['title']}")
    print(f"Author:      {post['author']}")
    print(f"Date:        {post['date']}")
    print(f"Description: {post['description']}")
    print("-" * 40)

def view_all_posts():
    """Displays all posts in the system."""
    print("\n--- All Posts ---")
    if not posts:
        print("No posts available yet.")
        return
        
    for post in posts:
        format_post(post)

def search_posts_by_username():
    """Allows searching for posts created by a specific username."""
    print("\n--- Search Posts ---")
    search_user = get_non_empty_input("Enter username to search for: ")
    
    found_posts = [post for post in posts if post['author'] == search_user]
    
    if not found_posts:
        print(f"No posts found for user '{search_user}'.")
    else:
        print(f"\n--- Posts by {search_user} ---")
        for post in found_posts:
            format_post(post)

def user_menu(username):
    """Displays the menu for logged-in users."""
    while True:
        print(f"\n--- Welcome to PostBoard, {username}! ---")
        print("1. Create a Post")
        print("2. View All Posts")
        print("3. Search Posts by Username")
        print("4. Logout")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            create_post(username)
        elif choice == '2':
            view_all_posts()
        elif choice == '3':
            search_posts_by_username()
        elif choice == '4':
            print(f"Logging out {username}...")
            break
        else:
            print("Error: Invalid choice. Please select a valid option.")

def main():
    """Main entry point of the PostBoard application."""
    print("===================================")
    print("      Welcome to PostBoard         ")
    print("===================================")
    while True:
        print("\n=== Main Menu ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            register_user()
        elif choice == '2':
            logged_in_user = login_user()
            if logged_in_user:
                user_menu(logged_in_user)
        elif choice == '3':
            print("Exiting PostBoard. Goodbye!")
            break
        else:
            print("Error: Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
