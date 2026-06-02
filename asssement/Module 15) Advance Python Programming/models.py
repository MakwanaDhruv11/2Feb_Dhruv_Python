import os
import re

# Custom exception for validation errors
class ValidationError(Exception):
    pass

class User:
    """Represents a blog user."""
    def __init__(self, username):
        self.username = self.validate(username)

    def validate(self, username):
        if not username or not username.strip():
            raise ValidationError("Author name is required and cannot be empty.")
        
        # Strip trailing/leading spaces
        name = username.strip()
        
        # Check for characters that shouldn't be in a filename
        if any(char in name for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            raise ValidationError("Author name cannot contain special characters like / \\ : * ? \" < > |")
        
        return name


class Post:
    """Represents a blog post containing title, content, and author."""
    def __init__(self, title, content, author):
        if not isinstance(author, User):
            raise ValidationError("Author must be a valid User object.")
            
        self.author = author
        self.title = self.validate_title(title)
        self.content = self.validate_content(content)

    def validate_title(self, title):
        if not title or not title.strip():
            raise ValidationError("Post title is required and cannot be empty.")
            
        t = title.strip()
        if any(char in t for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            raise ValidationError("Post title cannot contain special characters like / \\ : * ? \" < > |")
            
        return t

    def validate_content(self, content):
        if not content or not content.strip():
            raise ValidationError("Post content cannot be empty.")
            
        return content.strip()

    def get_filename(self):
        """Creates a safe filename using the username_title.txt format."""
        # Replace spaces in username and title with underscores for file safety
        safe_user = self.author.username.replace(' ', '_')
        safe_title = self.title.replace(' ', '_')
        return f"{safe_user}_{safe_title}.txt"

    def save_to_file(self, folder):
        """Saves the post details to a text file."""
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            
        filepath = os.path.join(folder, self.get_filename())
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(f"Author: {self.author.username}\n")
                file.write(f"Title: {self.title}\n")
                file.write("====================\n")
                file.write(self.content)
        except IOError as e:
            raise IOError(f"Error saving file: {e}")

    @staticmethod
    def load_from_file(filepath):
        """Reads a post file and reconstructs the Post object."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except IOError as e:
            raise IOError(f"Error reading file: {e}")

        # Basic parsing
        author_name = ""
        title = ""
        content_lines = []
        is_content = False
        
        for line in lines:
            if not is_content:
                if line.startswith("Author: "):
                    author_name = line[len("Author: "):].strip()
                elif line.startswith("Title: "):
                    title = line[len("Title: "):].strip()
                elif line.startswith("==="):
                    is_content = True
            else:
                content_lines.append(line)
                
        if not author_name or not title:
            raise ValidationError("Could not parse file. The file format is invalid.")
            
        content = "".join(content_lines)
        return Post(title, content, User(author_name))
