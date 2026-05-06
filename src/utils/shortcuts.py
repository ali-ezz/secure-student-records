"""
⌨️ Keyboard Shortcuts Manager
Global keyboard shortcuts for the application
"""

import tkinter as tk
from tkinter import messagebox


class KeyboardShortcuts:
    """Manages keyboard shortcuts for the application"""
    
    # Shortcut definitions
    SHORTCUTS = {
        '<Control-n>': {
            'name': 'New Record',
            'description': 'Create new record',
            'icon': '➕'
        },
        '<Control-f>': {
            'name': 'Search',
            'description': 'Focus search bar',
            'icon': '🔍'
        },
        '<Control-e>': {
            'name': 'Export',
            'description': 'Export current view',
            'icon': '📊'
        },
        '<Control-r>': {
            'name': 'Refresh',
            'description': 'Refresh data',
            'icon': '🔄'
        },
        '<Control-s>': {
            'name': 'Save',
            'description': 'Save changes',
            'icon': '💾'
        },
        '<F1>': {
            'name': 'Help',
            'description': 'Show help',
            'icon': '❓'
        },
        '<Alt-l>': {
            'name': 'Logout',
            'description': 'Logout from application',
            'icon': '🚪'
        },
        '<Control-q>': {
            'name': 'Quit',
            'description': 'Exit application',
            'icon': '❌'
        },
        '<Control-comma>': {
            'name': 'Settings',
            'description': 'Open settings',
            'icon': '⚙️'
        },
        '<Escape>': {
            'name': 'Close/Cancel',
            'description': 'Close dialog or cancel action',
            'icon': '⏎'
        }
    }
    
    def __init__(self, root):
        """
        Initialize keyboard shortcuts
        
        Args:
            root: Main Tk window
        """
        self.root = root
        self.callbacks = {}
        self.enabled = True
    
    def bind(self, shortcut, callback):
        """
        Bind a shortcut to a callback
        
        Args:
            shortcut: Shortcut key (e.g., '<Control-n>')
            callback: Function to call
        """
        if shortcut not in self.SHORTCUTS:
            print(f"Warning: Unknown shortcut {shortcut}")
            return
        
        self.callbacks[shortcut] = callback
        self.root.bind(shortcut, lambda e: self._handle_shortcut(shortcut, e))
    
    def unbind(self, shortcut):
        """Unbind a shortcut"""
        if shortcut in self.callbacks:
            del self.callbacks[shortcut]
            self.root.unbind(shortcut)
    
    def _handle_shortcut(self, shortcut, event):
        """Handle shortcut press"""
        if not self.enabled:
            return
        
        if shortcut in self.callbacks:
            try:
                self.callbacks[shortcut]()
            except Exception as e:
                print(f"Error executing shortcut {shortcut}: {e}")
    
    def enable(self):
        """Enable shortcuts"""
        self.enabled = True
    
    def disable(self):
        """Disable shortcuts"""
        self.enabled = False
    
    def show_help(self):
        """Show shortcuts help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("⌨️ Keyboard Shortcuts")
        help_window.geometry("500x600")
        help_window.resizable(False, False)
        
        # Center window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() - 500) // 2
        y = (help_window.winfo_screenheight() - 600) // 2
        help_window.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(help_window, bg='#4361ee', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⌨️ Keyboard Shortcuts",
            font=('Segoe UI', 18, 'bold'),
            bg='#4361ee',
            fg='white'
        ).pack(expand=True)
        
        # Shortcuts list
        canvas = tk.Canvas(help_window)
        scrollbar = tk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add shortcuts
        for shortcut, info in self.SHORTCUTS.items():
            frame = tk.Frame(scrollable_frame, bg='white', pady=10)
            frame.pack(fill='x', padx=20, pady=5)
            
            # Icon
            tk.Label(
                frame,
                text=info['icon'],
                font=('Segoe UI', 20),
                bg='white'
            ).pack(side='left', padx=10)
            
            # Info
            info_frame = tk.Frame(frame, bg='white')
            info_frame.pack(side='left', fill='x', expand=True)
            
            tk.Label(
                info_frame,
                text=info['name'],
                font=('Segoe UI', 12, 'bold'),
                bg='white',
                anchor='w'
            ).pack(fill='x')
            
            tk.Label(
                info_frame,
                text=info['description'],
                font=('Segoe UI', 10),
                bg='white',
                fg='gray',
                anchor='w'
            ).pack(fill='x')
            
            # Shortcut key
            key_text = shortcut.replace('<', '').replace('>', '').replace('-', ' + ')
            tk.Label(
                frame,
                text=key_text,
                font=('Segoe UI', 10, 'bold'),
                bg='#e0e0e0',
                fg='#333',
                padx=10,
                pady=5
            ).pack(side='right', padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        tk.Button(
            help_window,
            text="Close",
            font=('Segoe UI', 11),
            bg='#4361ee',
            fg='white',
            relief='flat',
            padx=30,
            pady=10,
            command=help_window.destroy
        ).pack(pady=20)


class ShortcutManager:
    """
    Simplified shortcut manager for dashboards
    Usage:
        sm = ShortcutManager(self, root)
        sm.register_search(search_func)
        sm.register_export(export_func)
        sm.register_refresh(refresh_func)
    """
    
    def __init__(self, dashboard, root):
        self.dashboard = dashboard
        self.root = root
        self.kbd = KeyboardShortcuts(root)
    
    def register_search(self, callback):
        """Register Ctrl+F for search"""
        self.kbd.bind('<Control-f>', callback)
    
    def register_export(self, callback):
        """Register Ctrl+E for export"""
        self.kbd.bind('<Control-e>', callback)
    
    def register_refresh(self, callback):
        """Register Ctrl+R for refresh"""
        self.kbd.bind('<Control-r>', callback)
    
    def register_new(self, callback):
        """Register Ctrl+N for new record"""
        self.kbd.bind('<Control-n>', callback)
    
    def register_save(self, callback):
        """Register Ctrl+S for save"""
        self.kbd.bind('<Control-s>', callback)
    
    def register_help(self, callback=None):
        """Register F1 for help"""
        if callback:
            self.kbd.bind('<F1>', callback)
        else:
            self.kbd.bind('<F1>', self.kbd.show_help)
    
    def register_logout(self, callback):
        """Register Alt+L for logout"""
        self.kbd.bind('<Alt-l>', callback)
    
    def show_help(self):
        """Show help dialog"""
        self.kbd.show_help()


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("Keyboard Shortcuts Test")
    root.geometry("400x300")
    
    kbd = KeyboardShortcuts(root)
    
    kbd.bind('<Control-n>', lambda: print("New Record"))
    kbd.bind('<Control-f>', lambda: print("Search"))
    kbd.bind('<Control-e>', lambda: print("Export"))
    kbd.bind('<F1>', kbd.show_help)
    
    tk.Label(
        root,
        text="Press keyboard shortcuts:\n\n"
             "Ctrl+N - New Record\n"
             "Ctrl+F - Search\n"
             "Ctrl+E - Export\n"
             "F1 - Help",
        font=('Segoe UI', 12),
        justify='left'
    ).pack(expand=True)
    
    tk.Button(
        root,
        text="Show All Shortcuts (F1)",
        command=kbd.show_help
    ).pack(pady=20)
    
    root.mainloop()
