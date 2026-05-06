"""
SRMS - Premium Modern Theme System
Glass Morphism, Multiple Color Themes, Smooth Animations
"""

import tkinter as tk
from tkinter import ttk
import colorsys


class ColorThemes:
    """Multiple color themes for the application."""
    
    DARK = {
        'name': 'Dark',
        'bg_primary': '#000000',
        'bg_secondary': '#0a0a0a',
        'bg_card': '#1a1a1a',
        'bg_glass': 'rgba(255,255,255,0.05)',
        'text_primary': '#ffffff',
        'text_secondary': '#a0a0a0',
        'accent': '#3b82f6',
        'accent_hover': '#60a5fa',
        'accent_glow': '#3b82f6',
        'border': '#1f1f1f',
        'success': '#22c55e',
        'warning': '#eab308',
        'error': '#ef4444',
        'gradient_start': '#1a1a2e',
        'gradient_end': '#16213e',
    }
    
    LIGHT = {
        'name': 'Light',
        'bg_primary': '#ffffff',
        'bg_secondary': '#f8fafc',
        'bg_card': '#ffffff',
        'bg_glass': 'rgba(0,0,0,0.03)',
        'text_primary': '#000000',
        'text_secondary': '#64748b',
        'accent': '#3b82f6',
        'accent_hover': '#2563eb',
        'accent_glow': '#93c5fd',
        'border': '#e2e8f0',
        'success': '#16a34a',
        'warning': '#ca8a04',
        'error': '#dc2626',
        'gradient_start': '#f0f9ff',
        'gradient_end': '#e0f2fe',
    }
    
    SOLARIZED = {
        'name': 'Solarized',
        'bg_primary': '#002b36',
        'bg_secondary': '#073642',
        'bg_card': '#073642',
        'bg_glass': 'rgba(147,161,161,0.08)',
        'text_primary': '#93a1a1',
        'text_secondary': '#657b83',
        'accent': '#268bd2',
        'accent_hover': '#2aa198',
        'accent_glow': '#268bd2',
        'border': '#586e75',
        'success': '#859900',
        'warning': '#b58900',
        'error': '#dc322f',
        'gradient_start': '#002b36',
        'gradient_end': '#073642',
    }
    
    NORD = {
        'name': 'Nord',
        'bg_primary': '#2e3440',
        'bg_secondary': '#3b4252',
        'bg_card': '#3b4252',
        'bg_glass': 'rgba(236,239,244,0.06)',
        'text_primary': '#eceff4',
        'text_secondary': '#d8dee9',
        'accent': '#88c0d0',
        'accent_hover': '#81a1c1',
        'accent_glow': '#88c0d0',
        'border': '#4c566a',
        'success': '#a3be8c',
        'warning': '#ebcb8b',
        'error': '#bf616a',
        'gradient_start': '#2e3440',
        'gradient_end': '#3b4252',
    }
    
    @classmethod
    def get_all(cls):
        return [cls.DARK, cls.LIGHT, cls.SOLARIZED, cls.NORD]
    
    @classmethod
    def get_by_name(cls, name):
        themes = {t['name']: t for t in cls.get_all()}
        return themes.get(name, cls.DARK)


class ModernStyle:
    """Modern style configuration for Tkinter widgets."""
    
    def __init__(self, theme=None):
        self.theme = theme or ColorThemes.DARK
        self.style = None
    
    def apply(self, root):
        """Apply modern theme to root window and all widgets."""
        self.style = ttk.Style(root)
        
        # Use clam as base theme
        self.style.theme_use('clam')
        
        # Configure all widget styles
        self._configure_frames()
        self._configure_labels()
        self._configure_buttons()
        self._configure_entries()
        self._configure_treeview()
        self._configure_notebook()
        self._configure_scrollbar()
        self._configure_separator()
        self._configure_combobox()
        self._configure_labelframe()
        
        # Configure root window
        root.configure(bg=self.theme['bg_primary'])
        
        return self.style
    
    def _configure_frames(self):
        """Configure frame styles."""
        self.style.configure('TFrame',
            background=self.theme['bg_primary']
        )
        
        # Glass card style
        self.style.configure('Card.TFrame',
            background=self.theme['bg_card'],
            relief='flat'
        )
        
        # Sidebar style
        self.style.configure('Sidebar.TFrame',
            background=self.theme['bg_secondary']
        )
    
    def _configure_labels(self):
        """Configure label styles."""
        self.style.configure('TLabel',
            background=self.theme['bg_primary'],
            foreground=self.theme['text_primary'],
            font=('Segoe UI', 11)
        )
        
        # Title style
        self.style.configure('Title.TLabel',
            background=self.theme['bg_primary'],
            foreground=self.theme['text_primary'],
            font=('Segoe UI', 24, 'bold')
        )
        
        # Subtitle style
        self.style.configure('Subtitle.TLabel',
            background=self.theme['bg_primary'],
            foreground=self.theme['text_secondary'],
            font=('Segoe UI', 12)
        )
        
        # Secondary text
        self.style.configure('Secondary.TLabel',
            background=self.theme['bg_primary'],
            foreground=self.theme['text_secondary'],
            font=('Segoe UI', 10)
        )
        
        # Accent label
        self.style.configure('Accent.TLabel',
            background=self.theme['bg_primary'],
            foreground=self.theme['accent'],
            font=('Segoe UI', 11)
        )
        
        # Card label
        self.style.configure('Card.TLabel',
            background=self.theme['bg_card'],
            foreground=self.theme['text_primary'],
            font=('Segoe UI', 11)
        )
    
    def _configure_buttons(self):
        """Configure button styles."""
        # Primary button
        self.style.configure('TButton',
            background=self.theme['accent'],
            foreground='#ffffff',
            font=('Segoe UI', 11),
            padding=(16, 8),
            borderwidth=0,
            focuscolor=self.theme['accent']
        )
        self.style.map('TButton',
            background=[
                ('active', self.theme['accent_hover']),
                ('pressed', self.theme['accent']),
            ],
            foreground=[('active', '#ffffff')]
        )
        
        # Secondary button
        self.style.configure('Secondary.TButton',
            background=self.theme['bg_card'],
            foreground=self.theme['text_primary'],
            font=('Segoe UI', 11),
            padding=(16, 8),
            borderwidth=1
        )
        self.style.map('Secondary.TButton',
            background=[
                ('active', self.theme['bg_secondary']),
            ]
        )
        
        # Ghost button (transparent)
        self.style.configure('Ghost.TButton',
            background=self.theme['bg_primary'],
            foreground=self.theme['text_secondary'],
            font=('Segoe UI', 10),
            padding=(8, 4),
            borderwidth=0
        )
        self.style.map('Ghost.TButton',
            foreground=[('active', self.theme['accent'])]
        )
        
        # Success button
        self.style.configure('Success.TButton',
            background=self.theme['success'],
            foreground='#ffffff',
            font=('Segoe UI', 11),
            padding=(16, 8)
        )
        
        # Danger button
        self.style.configure('Danger.TButton',
            background=self.theme['error'],
            foreground='#ffffff',
            font=('Segoe UI', 11),
            padding=(16, 8)
        )
        
        # Nav button (sidebar)
        self.style.configure('Nav.TButton',
            background=self.theme['bg_secondary'],
            foreground=self.theme['text_secondary'],
            font=('Segoe UI', 11),
            padding=(12, 10),
            anchor='w'
        )
        self.style.map('Nav.TButton',
            background=[
                ('active', self.theme['accent']),
                ('selected', self.theme['accent']),
            ],
            foreground=[
                ('active', '#ffffff'),
                ('selected', '#ffffff'),
            ]
        )
    
    def _configure_entries(self):
        """Configure entry styles."""
        self.style.configure('TEntry',
            fieldbackground=self.theme['bg_card'],
            foreground=self.theme['text_primary'],
            insertcolor=self.theme['accent'],
            borderwidth=1,
            relief='flat',
            padding=(10, 8)
        )
        self.style.map('TEntry',
            fieldbackground=[('focus', self.theme['bg_secondary'])]
        )
    
    def _configure_treeview(self):
        """Configure treeview styles."""
        self.style.configure('Treeview',
            background=self.theme['bg_card'],
            foreground=self.theme['text_primary'],
            fieldbackground=self.theme['bg_card'],
            borderwidth=0,
            rowheight=32,
            font=('Segoe UI', 10)
        )
        self.style.configure('Treeview.Heading',
            background=self.theme['bg_secondary'],
            foreground=self.theme['text_primary'],
            font=('Segoe UI', 10, 'bold'),
            borderwidth=0,
            relief='flat'
        )
        self.style.map('Treeview',
            background=[('selected', self.theme['accent'])],
            foreground=[('selected', '#ffffff')]
        )
    
    def _configure_notebook(self):
        """Configure notebook (tabs) styles."""
        self.style.configure('TNotebook',
            background=self.theme['bg_primary'],
            borderwidth=0,
            tabmargins=[0, 0, 0, 0]
        )
        self.style.configure('TNotebook.Tab',
            background=self.theme['bg_secondary'],
            foreground=self.theme['text_secondary'],
            padding=[16, 10],
            font=('Segoe UI', 10),
            borderwidth=0
        )
        self.style.map('TNotebook.Tab',
            background=[
                ('selected', self.theme['bg_primary']),
                ('active', self.theme['bg_card']),
            ],
            foreground=[
                ('selected', self.theme['accent']),
                ('active', self.theme['text_primary']),
            ]
        )
    
    def _configure_scrollbar(self):
        """Configure scrollbar styles."""
        self.style.configure('Vertical.TScrollbar',
            background=self.theme['bg_secondary'],
            troughcolor=self.theme['bg_primary'],
            borderwidth=0,
            arrowsize=0,
            width=8
        )
        self.style.map('Vertical.TScrollbar',
            background=[('active', self.theme['accent'])]
        )
    
    def _configure_separator(self):
        """Configure separator styles."""
        self.style.configure('TSeparator',
            background=self.theme['border']
        )
    
    def _configure_combobox(self):
        """Configure combobox styles."""
        self.style.configure('TCombobox',
            fieldbackground=self.theme['bg_card'],
            background=self.theme['bg_card'],
            foreground=self.theme['text_primary'],
            arrowcolor=self.theme['text_secondary'],
            borderwidth=1,
            padding=(8, 6)
        )
        self.style.map('TCombobox',
            fieldbackground=[('readonly', self.theme['bg_card'])],
            selectbackground=[('focus', self.theme['accent'])]
        )
    
    def _configure_labelframe(self):
        """Configure labelframe styles."""
        self.style.configure('TLabelframe',
            background=self.theme['bg_card'],
            bordercolor=self.theme['border'],
            lightcolor=self.theme['border'],
            darkcolor=self.theme['border']
        )
        self.style.configure('TLabelframe.Label',
            background=self.theme['bg_card'],
            foreground=self.theme['accent'],
            font=('Segoe UI', 11, 'bold')
        )


class GlassCard(ttk.Frame):
    """Glass morphism style card widget."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style='Card.TFrame', **kwargs)
        self.configure(padding=20)


class ToastNotification:
    """Modern toast notification system."""
    
    def __init__(self, root, theme=None):
        self.root = root
        self.theme = theme or ColorThemes.DARK
        self.toasts = []
    
    def show(self, message, type_='info', duration=3000):
        """Show a toast notification."""
        colors = {
            'info': self.theme['accent'],
            'success': self.theme['success'],
            'warning': self.theme['warning'],
            'error': self.theme['error'],
        }
        
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
        }
        
        # Create toast window
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        
        # Position at bottom right
        x = self.root.winfo_x() + self.root.winfo_width() - 320
        y = self.root.winfo_y() + self.root.winfo_height() - 80 - (len(self.toasts) * 70)
        toast.geometry(f'300x60+{x}+{y}')
        
        # Style
        toast.configure(bg=self.theme['bg_card'])
        
        # Content frame
        frame = tk.Frame(toast, bg=self.theme['bg_card'], highlightthickness=1,
                        highlightbackground=colors.get(type_, self.theme['accent']))
        frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Icon and message
        tk.Label(frame, text=icons.get(type_, 'ℹ️'), font=('Segoe UI', 16),
                bg=self.theme['bg_card'], fg=colors.get(type_, self.theme['accent'])).pack(side='left', padx=10)
        
        tk.Label(frame, text=message, font=('Segoe UI', 11),
                bg=self.theme['bg_card'], fg=self.theme['text_primary'],
                wraplength=220).pack(side='left', fill='x', expand=True, padx=5)
        
        # Close button
        close_btn = tk.Label(frame, text='×', font=('Segoe UI', 14),
                            bg=self.theme['bg_card'], fg=self.theme['text_secondary'],
                            cursor='hand2')
        close_btn.pack(side='right', padx=10)
        close_btn.bind('<Button-1>', lambda e: self._close_toast(toast))
        
        self.toasts.append(toast)
        
        # Auto close
        self.root.after(duration, lambda: self._close_toast(toast))
    
    def _close_toast(self, toast):
        """Close a toast notification."""
        if toast in self.toasts:
            self.toasts.remove(toast)
        try:
            toast.destroy()
        except:
            pass


class AnimatedBackground:
    """Simple animated gradient background effect."""
    
    def __init__(self, canvas, theme=None):
        self.canvas = canvas
        self.theme = theme or ColorThemes.DARK
        self.phase = 0
    
    def draw(self):
        """Draw gradient background."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Simple gradient
        start = self.theme['gradient_start']
        end = self.theme['gradient_end']
        
        # Draw gradient lines
        steps = 50
        for i in range(steps):
            ratio = i / steps
            color = self._interpolate_color(start, end, ratio)
            y1 = int(height * ratio)
            y2 = int(height * (ratio + 1/steps))
            self.canvas.create_rectangle(0, y1, width, y2, fill=color, outline=color)
    
    def _interpolate_color(self, color1, color2, ratio):
        """Interpolate between two hex colors."""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        return f'#{r:02x}{g:02x}{b:02x}'


# Theme manager singleton
_current_theme = ColorThemes.DARK
_style_instance = None
_toast_manager = None


def get_theme():
    """Get current theme."""
    return _current_theme


def set_theme(theme):
    """Set current theme."""
    global _current_theme
    _current_theme = theme


def apply_theme(root, theme_name='Dark'):
    """Apply theme to application."""
    global _current_theme, _style_instance, _toast_manager
    
    _current_theme = ColorThemes.get_by_name(theme_name)
    _style_instance = ModernStyle(_current_theme)
    _style_instance.apply(root)
    _toast_manager = ToastNotification(root, _current_theme)
    
    return _style_instance


def get_toast_manager():
    """Get toast notification manager."""
    return _toast_manager


def show_toast(message, type_='info'):
    """Show a toast notification."""
    if _toast_manager:
        _toast_manager.show(message, type_)
