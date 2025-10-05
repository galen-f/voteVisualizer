# config.py

# Just a dumb color dict – keep it simple
COLORS = {
    "yes": "#2ca02c",
    "no": "#d62728",
    "present": "#ff7f0e",
    "not_voting": "#7f7f7f",

    "lines": "#0D0D0D"
}

STYLES = {
    "default": 0.5,
    "bold": 0.5,
    "faint": 0.1,
}

def color_for(key: str) -> str:
    """Get a color by a simple name like 'yes', 'no', 'present', 'not_voting'."""
    return COLORS[key]

def style_for(key: str) -> str:
    """Get a style value by a simple name like 'default', 'bold', 'faint'."""
    return STYLES[key]