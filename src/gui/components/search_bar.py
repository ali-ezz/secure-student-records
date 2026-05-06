"""
🔍 Advanced Search Bar Component
Reusable search widget with real-time filtering
"""

import tkinter as tk
from tkinter import ttk


class SearchBar(ttk.Frame):
    """Advanced search bar with filtering capabilities"""
    
    def __init__(self, parent, on_search_callback, placeholder="Search...", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_search = on_search_callback
        self.placeholder = placeholder
        
        self._create_ui()
    
    def _create_ui(self):
        """Create search bar UI"""
        # Search icon/label
        self.search_label = ttk.Label(self, text="🔍", font=('Segoe UI', 12))
        self.search_label.pack(side='left', padx=(5, 0))
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_text_change)
        
        self.search_entry = ttk.Entry(
            self, 
            textvariable=self.search_var,
            font=('Segoe UI', 11),
            width=40
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Placeholder handling
        self.search_entry.insert(0, self.placeholder)
        self.search_entry.bind('<FocusIn>', self._on_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_focus_out)
        self.search_entry.config(foreground='gray')
        
        # Clear button
        self.clear_btn = ttk.Button(
            self,
            text="✕",
            width=3,
            command=self.clear
        )
        self.clear_btn.pack(side='left', padx=(0, 5))
        
        # Initially hide clear button
        self.clear_btn.pack_forget()
    
    def _on_focus_in(self, event):
        """Remove placeholder on focus"""
        if self.search_entry.get() == self.placeholder:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground='black')
    
    def _on_focus_out(self, event):
        """Restore placeholder if empty"""
        if not self.search_entry.get():
            self.search_entry.insert(0, self.placeholder)
            self.search_entry.config(foreground='gray')
    
    def _on_text_change(self, *args):
        """Handle text changes"""
        text = self.search_var.get()
        
        # Show/hide clear button (check if it exists first)
        if hasattr(self, 'clear_btn'):
            if text and text != self.placeholder:
                if not self.clear_btn.winfo_ismapped():
                    self.clear_btn.pack(side='left', padx=(0, 5))
            else:
                if self.clear_btn.winfo_ismapped():
                    self.clear_btn.pack_forget()
        
        # Call search callback (only if not placeholder)
        if text != self.placeholder:
            self.on_search(text)
    
    def get(self):
        """Get search text"""
        text = self.search_var.get()
        return text if text != self.placeholder else ""
    
    def clear(self):
        """Clear search"""
        self.search_var.set("")
        self.search_entry.focus()
    
    def focus(self):
        """Focus search entry"""
        self.search_entry.focus()


class AdvancedSearchDialog(tk.Toplevel):
    """Advanced search dialog with multiple filters"""
    
    def __init__(self, parent, on_search_callback):
        super().__init__(parent)
        
        self.on_search = on_search_callback
        self.title("Advanced Search")
        self.geometry("500x400")
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 400) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_ui()
    
    def _create_ui(self):
        """Create advanced search UI"""
        # Header
        header = ttk.Label(
            self,
            text="🔍 Advanced Search",
            font=('Segoe UI', 16, 'bold')
        )
        header.pack(pady=20)
        
        # Search fields
        fields_frame = ttk.Frame(self)
        fields_frame.pack(fill='both', expand=True, padx=20)
        
        # Text search
        ttk.Label(fields_frame, text="Search Text:").grid(row=0, column=0, sticky='w', pady=5)
        self.text_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.text_var, width=40).grid(row=0, column=1, pady=5)
        
        # Date range
        ttk.Label(fields_frame, text="Date From:").grid(row=1, column=0, sticky='w', pady=5)
        self.date_from_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.date_from_var, width=20).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(fields_frame, text="Date To:").grid(row=2, column=0, sticky='w', pady=5)
        self.date_to_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.date_to_var, width=20).grid(row=2, column=1, sticky='w', pady=5)
        
        # Status filter
        ttk.Label(fields_frame, text="Status:").grid(row=3, column=0, sticky='w', pady=5)
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            fields_frame,
            textvariable=self.status_var,
            values=['All', 'Active', 'Inactive', 'Pending', 'Approved', 'Denied'],
            width=20
        )
        status_combo.grid(row=3, column=1, sticky='w', pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame, text="Search", command=self._do_search).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side='right', padx=5)
    
    def _do_search(self):
        """Execute search"""
        filters = {
            'text': self.text_var.get(),
            'date_from': self.date_from_var.get(),
            'date_to': self.date_to_var.get(),
            'status': self.status_var.get() if self.status_var.get() != 'All' else None
        }
        
        self.on_search(filters)
        self.destroy()
    
    def _clear(self):
        """Clear all fields"""
        self.text_var.set("")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.status_var.set("All")


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("Search Bar Test")
    root.geometry("600x400")
    
    def on_search(text):
        print(f"Searching for: {text}")
    
    search = SearchBar(root, on_search)
    search.pack(fill='x', padx=20, pady=20)
    
    ttk.Label(root, text="Type to search...").pack(pady=20)
    
    root.mainloop()
