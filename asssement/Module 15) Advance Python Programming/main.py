import os
import tkinter as tk
from tkinter import messagebox
from models import User, Post, ValidationError

class MiniBlogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniBlog - Desktop Journal Application")
        self.root.geometry("800x550")
        
        # Configure overall window color
        self.root.configure(bg="#f0f2f5")
        
        # Define directory for saving posts
        self.posts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts")
        if not os.path.exists(self.posts_dir):
            os.makedirs(self.posts_dir, exist_ok=True)
            
        # Store file paths mapping to listbox indexes
        self.post_files = []
        
        # Build UI layout
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # 1. Title Banner
        banner_frame = tk.Frame(self.root, bg="#3b5998", height=60)
        banner_frame.pack(fill="x", side="top")
        
        title_label = tk.Label(
            banner_frame, 
            text="MiniBlog Dashboard", 
            font=("Arial", 16, "bold"), 
            fg="white", 
            bg="#3b5998"
        )
        title_label.pack(pady=15)

        # 2. Main Content Container
        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 3. Left Panel - Saved Posts list
        left_panel = tk.Frame(main_frame, bg="#f0f2f5")
        left_panel.pack(side="left", fill="both", expand=False)
        
        lbl_saved = tk.Label(
            left_panel, 
            text="Saved Blog Posts", 
            font=("Arial", 11, "bold"), 
            bg="#f0f2f5", 
            fg="#333"
        )
        lbl_saved.pack(anchor="w", pady=(0, 5))

        list_container = tk.Frame(left_panel)
        list_container.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            list_container, 
            font=("Arial", 10), 
            selectbackground="#3b5998", 
            selectforeground="white",
            width=28
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select_post)

        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Sidebar Buttons
        sidebar_buttons = tk.Frame(left_panel, bg="#f0f2f5")
        sidebar_buttons.pack(fill="x", pady=10)

        self.btn_refresh = tk.Button(
            sidebar_buttons, 
            text="Refresh", 
            command=self.refresh_list, 
            bg="#e4e6eb", 
            font=("Arial", 9)
        )
        self.btn_refresh.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_delete = tk.Button(
            sidebar_buttons, 
            text="Delete Post", 
            command=self.delete_post, 
            bg="#f5c2c2", 
            font=("Arial", 9)
        )
        self.btn_delete.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Divider frame for spacing
        divider = tk.Frame(main_frame, width=15, bg="#f0f2f5")
        divider.pack(side="left", fill="y")

        # 4. Right Panel - Form inputs
        right_panel = tk.Frame(main_frame, bg="white", bd=1, relief="solid", padx=15, pady=15)
        right_panel.pack(side="right", fill="both", expand=True)

        tk.Label(
            right_panel, 
            text="Create / Edit Blog Post", 
            font=("Arial", 12, "bold"), 
            bg="white", 
            fg="#3b5998"
        ).pack(anchor="w", pady=(0, 15))

        # Author Name
        tk.Label(right_panel, text="Author Name:", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=2)
        self.entry_author = tk.Entry(right_panel, font=("Arial", 10), bd=1, relief="solid")
        self.entry_author.pack(fill="x", pady=(0, 10))

        # Post Title
        tk.Label(right_panel, text="Post Title:", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=2)
        self.entry_title = tk.Entry(right_panel, font=("Arial", 10), bd=1, relief="solid")
        self.entry_title.pack(fill="x", pady=(0, 10))

        # Content Text Box
        tk.Label(right_panel, text="Post Content:", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=2)
        
        content_container = tk.Frame(right_panel)
        content_container.pack(fill="both", expand=True, pady=(0, 15))

        self.text_content = tk.Text(
            content_container, 
            font=("Arial", 10), 
            wrap="word", 
            bd=1, 
            relief="solid"
        )
        self.text_content.pack(side="left", fill="both", expand=True)

        text_scroll = tk.Scrollbar(content_container, orient="vertical", command=self.text_content.yview)
        text_scroll.pack(side="right", fill="y")
        self.text_content.config(yscrollcommand=text_scroll.set)

        # Form Buttons
        form_buttons = tk.Frame(right_panel, bg="white")
        form_buttons.pack(fill="x")

        self.btn_clear = tk.Button(
            form_buttons, 
            text="Clear Fields", 
            command=self.clear_fields, 
            bg="#e4e6eb", 
            font=("Arial", 10),
            width=15
        )
        self.btn_clear.pack(side="left", pady=5)

        self.btn_save = tk.Button(
            form_buttons, 
            text="Save Post", 
            command=self.save_post, 
            bg="#3b5998", 
            fg="white", 
            font=("Arial", 10, "bold"),
            width=15
        )
        self.btn_save.pack(side="right", pady=5)

    def clear_fields(self):
        """Resets the input form back to blank."""
        self.entry_author.config(state="normal")
        self.entry_title.config(state="normal")
        
        self.entry_author.delete(0, tk.END)
        self.entry_title.delete(0, tk.END)
        self.text_content.delete("1.0", tk.END)
        
        self.listbox.selection_clear(0, tk.END)

    def refresh_list(self):
        """Scans the saved folder and updates the listbox."""
        self.listbox.delete(0, tk.END)
        self.post_files = []
        
        if not os.path.exists(self.posts_dir):
            return

        for filename in os.listdir(self.posts_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.posts_dir, filename)
                try:
                    # Quick parse to get display info
                    post = Post.load_from_file(filepath)
                    display_text = f"{post.title} (by {post.author.username})"
                    
                    self.listbox.insert(tk.END, display_text)
                    self.post_files.append(filepath)
                except Exception:
                    # Skip files that are corrupted or have a different format
                    continue

    def on_select_post(self, event):
        """Loads the selected post details into the editor form."""
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        filepath = self.post_files[index]

        try:
            post = Post.load_from_file(filepath)
            
            # Clear current contents
            self.entry_author.config(state="normal")
            self.entry_title.config(state="normal")
            
            self.entry_author.delete(0, tk.END)
            self.entry_title.delete(0, tk.END)
            self.text_content.delete("1.0", tk.END)
            
            # Insert loaded values
            self.entry_author.insert(0, post.author.username)
            self.entry_title.insert(0, post.title)
            self.text_content.insert("1.0", post.content)
            
            # Keep primary key fields disabled to prevent conflicting file rewrites
            self.entry_author.config(state="disabled")
            self.entry_title.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load post: {e}")

    def save_post(self):
        """Validates fields, creates classes and saves post to file."""
        author_name = self.entry_author.get()
        title = self.entry_title.get()
        content = self.text_content.get("1.0", tk.END).strip()

        try:
            # Validate and create objects
            user = User(author_name)
            post = Post(title, content, user)
            
            # Save post file
            post.save_to_file(self.posts_dir)
            
            messagebox.showinfo("Success", f"Post '{title}' saved successfully!")
            
            self.clear_fields()
            self.refresh_list()
            
        except ValidationError as e:
            messagebox.showwarning("Validation Error", str(e))
        except IOError as e:
            messagebox.showerror("File Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Failed to save post: {e}")

    def delete_post(self):
        """Deletes the highlighted post from the disk."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Required", "Please select a post from the list to delete.")
            return

        index = selection[0]
        filepath = self.post_files[index]

        confirm = messagebox.askyesno(
            "Confirm Delete", 
            "Are you sure you want to permanently delete this post?"
        )
        if not confirm:
            return

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                
            messagebox.showinfo("Success", "Post deleted successfully.")
            self.clear_fields()
            self.refresh_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete post: {e}")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MiniBlogApp(root)
    root.mainloop()
