# UI Styling constants
COLORS = {
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'dark': '#2c3e50',
    'light': '#ecf0f1',
    'white': '#ffffff',
    'black': '#000000'
}

FONTS = {
    'title': ('Arial', 24, 'bold'),
    'heading': ('Arial', 16, 'bold'),
    'normal': ('Arial', 11),
    'small': ('Arial', 9)
}

STYLES = {
    'button': {
        'padx': 20,
        'pady': 10,
        'font': FONTS['normal']
    },
    'frame': {
        'bg': COLORS['white'],
        'relief': 'raised',
        'bd': 2
    }
}