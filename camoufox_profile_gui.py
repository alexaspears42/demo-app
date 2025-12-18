#!/usr/bin/env python3
"""
Camoufox Profile Manager GUI
A simple tkinter-based GUI for managing Camoufox browser profiles.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import sys
import os
import json
from pathlib import Path
import threading


class CamoufoxProfileGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Camoufox Profile Manager")
        self.root.geometry("900x600")
        
        # Set the working directory to the project root
        self.project_root = Path(__file__).parent
        os.chdir(self.project_root)
        
        # Python executable path
        self.python_path = self.project_root / ".venv" / "bin" / "python"
        self.script_path = self.project_root / "scripts" / "manage_camoufox_profiles.py"
        
        self.setup_ui()
        self.refresh_profiles()
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Camoufox Profile Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Profiles list
        list_frame = ttk.LabelFrame(main_frame, text="Profiles", padding="5")
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for profiles
        columns = ("ID", "Name", "Storage Path", "Proxy")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Storage Path", text="Storage Path")
        self.tree.heading("Proxy", text="Proxy")
        
        self.tree.column("ID", width=280)
        self.tree.column("Name", width=120)
        self.tree.column("Storage Path", width=350)
        self.tree.column("Proxy", width=80)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Buttons
        ttk.Button(buttons_frame, text="📝 Create Profile", command=self.create_profile, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="✏️ Edit Profile", command=self.edit_profile, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="🗑️ Delete Profile", command=self.delete_profile, width=15).grid(row=0, column=2, padx=5)
        ttk.Button(buttons_frame, text="🌐 Open Profile", command=self.open_profile, width=15).grid(row=0, column=3, padx=5)
        ttk.Button(buttons_frame, text="🔄 Refresh", command=self.refresh_profiles, width=15).grid(row=0, column=4, padx=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, padding="5")
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def set_status(self, message):
        """Update the status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def run_command(self, cmd, show_output=False):
        """Run a command and return the result"""
        try:
            self.set_status(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                if show_output and result.stdout.strip():
                    messagebox.showinfo("Command Output", result.stdout)
                return result.stdout
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                messagebox.showerror("Error", f"Command failed:\n{error_msg}")
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run command: {str(e)}")
            return None
        finally:
            self.set_status("Ready")
    
    def refresh_profiles(self):
        """Refresh the profiles list"""
        self.set_status("Refreshing profiles...")
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get profiles in JSON format
        cmd = [str(self.python_path), str(self.script_path), "list", "--json"]
        output = self.run_command(cmd)
        
        if output:
            try:
                profiles = json.loads(output)
                for profile in profiles:
                    proxy_status = "yes" if profile.get("proxy_host") else "no"
                    self.tree.insert("", tk.END, values=(
                        profile["id"],
                        profile["name"],
                        profile["storage_path"],
                        proxy_status
                    ))
                self.set_status(f"Loaded {len(profiles)} profiles")
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Failed to parse profiles: {str(e)}")
                self.set_status("Error loading profiles")
    
    def get_selected_profile(self):
        """Get the currently selected profile"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a profile first.")
            return None
        
        item = self.tree.item(selection[0])
        return {
            "id": item["values"][0],
            "name": item["values"][1],
            "storage_path": item["values"][2],
            "proxy": item["values"][3]
        }
    
    def create_profile(self):
        """Create a new profile"""
        dialog = ProfileDialog(self.root, title="Create New Profile")
        if dialog.result:
            name = dialog.result["name"]
            proxy = dialog.result["proxy"]
            storage_path = dialog.result["storage_path"]
            
            cmd = [str(self.python_path), str(self.script_path), "create", name]
            if proxy:
                cmd.extend(["--proxy", proxy])
            if storage_path:
                cmd.extend(["--storage-path", storage_path])
            
            if self.run_command(cmd):
                messagebox.showinfo("Success", f"Profile '{name}' created successfully!")
                self.refresh_profiles()
    
    def edit_profile(self):
        """Edit the selected profile"""
        profile = self.get_selected_profile()
        if not profile:
            return
        
        dialog = ProfileDialog(self.root, title="Edit Profile", initial_data={
            "name": profile["name"],
            "storage_path": profile["storage_path"] if profile["storage_path"] != "default" else "",
            "proxy": ""  # Don't pre-fill proxy for security
        })
        
        if dialog.result:
            cmd = [str(self.python_path), str(self.script_path), "edit", profile["id"]]
            
            if dialog.result["name"]:
                cmd.extend(["--name", dialog.result["name"]])
            if dialog.result["proxy"]:
                cmd.extend(["--proxy", dialog.result["proxy"]])
            if dialog.result["storage_path"]:
                cmd.extend(["--storage-path", dialog.result["storage_path"]])
            
            if self.run_command(cmd):
                messagebox.showinfo("Success", f"Profile '{profile['name']}' updated successfully!")
                self.refresh_profiles()
    
    def delete_profile(self):
        """Delete the selected profile"""
        profile = self.get_selected_profile()
        if not profile:
            return
        
        # Confirm deletion
        response = messagebox.askyesnocancel(
            "Confirm Deletion",
            f"Delete profile '{profile['name']}'?\n\n"
            f"Choose:\n"
            f"• Yes: Delete profile and remove storage directory\n"
            f"• No: Delete profile but keep storage directory\n"
            f"• Cancel: Don't delete anything"
        )
        
        if response is None:  # Cancel
            return
        
        cmd = [str(self.python_path), str(self.script_path), "delete", profile["id"]]
        if response:  # Yes - remove storage
            cmd.append("--remove-storage")
        
        if self.run_command(cmd):
            action = "and storage directory" if response else "but kept storage directory"
            messagebox.showinfo("Success", f"Profile '{profile['name']}' deleted {action}!")
            self.refresh_profiles()
    
    def open_profile(self):
        """Open the selected profile for manual login"""
        profile = self.get_selected_profile()
        if not profile:
            return
        
        def run_open():
            cmd = [str(self.python_path), str(self.script_path), "open", profile["id"]]
            self.run_command(cmd, show_output=True)
        
        # Run in a separate thread to avoid blocking the GUI
        threading.Thread(target=run_open, daemon=True).start()
        messagebox.showinfo("Opening Profile", f"Opening profile '{profile['name']}' for manual login...")


class ProfileDialog:
    def __init__(self, parent, title="Profile", initial_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.initial_data = initial_data or {}
        self.setup_dialog()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def setup_dialog(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name field
        ttk.Label(main_frame, text="Profile Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.initial_data.get("name", ""))
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        name_entry.focus()
        
        # Storage path field
        ttk.Label(main_frame, text="Storage Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(optional, leave empty for default)", font=("Arial", 8)).grid(row=1, column=1, sticky=tk.W)
        self.storage_var = tk.StringVar(value=self.initial_data.get("storage_path", ""))
        storage_entry = ttk.Entry(main_frame, textvariable=self.storage_var, width=40)
        storage_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Proxy field
        ttk.Label(main_frame, text="Proxy:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(format: host:port:username:password)", font=("Arial", 8)).grid(row=3, column=1, sticky=tk.W)
        self.proxy_var = tk.StringVar(value=self.initial_data.get("proxy", ""))
        proxy_entry = ttk.Entry(main_frame, textvariable=self.proxy_var, width=40, show="*")
        proxy_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Configure column weight
        main_frame.columnconfigure(1, weight=1)
        
        # Bind Enter key to OK
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def ok_clicked(self):
        """Handle OK button click"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Profile name is required!")
            return
        
        self.result = {
            "name": name,
            "storage_path": self.storage_var.get().strip(),
            "proxy": self.proxy_var.get().strip()
        }
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()


def main():
    """Main entry point"""
    # Check if we're in the right directory
    if not Path("scripts/manage_camoufox_profiles.py").exists():
        print("Error: This script must be run from the content-pin-generator directory")
        print("Current directory:", os.getcwd())
        sys.exit(1)
    
    # Check if virtual environment exists
    venv_python = Path(".venv/bin/python")
    if not venv_python.exists():
        print("Error: Virtual environment not found at .venv/bin/python")
        print("Please make sure the virtual environment is properly set up.")
        sys.exit(1)
    
    root = tk.Tk()
    app = CamoufoxProfileGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()