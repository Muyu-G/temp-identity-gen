# utils.py
import os
import logging
from logging.handlers import RotatingFileHandler
try:
    from colorama import init, Fore as fore, Back as back, Style as style
    init(convert=True, strip=False)
    COLORAMA_AVAILABLE = True
    logging.info("Colorama initialized successfully")
except ImportError:
    COLORAMA_AVAILABLE = False
    logging.warning("Colorama not installed, falling back to plain text output")
    class Fore:
        BLACK = ''
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''
    class Back:
        BLACK = ''
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        DIM = ''
        NORMAL = ''
        RESET_ALL = ''
    fore = Fore()
    back = Back()
    style = Style()

try:
    from pyfiglet import Figlet
    FIGLET_AVAILABLE = True
    logging.info("Pyfiglet initialized successfully")
except ImportError:
    FIGLET_AVAILABLE = False
    logging.warning("Pyfiglet not installed, falling back to plain text banner")

# Setup logging with rotation for large files
os.makedirs('logs/auto_logs', exist_ok=True)
handler = RotatingFileHandler('logs/auto_logs/identity_generator.log', maxBytes=5*1024*1024, backupCount=3)
logging.basicConfig(handlers=[handler], level=logging.INFO)

def print_banner():
    """Print a colorful ASCII art banner for the application using standard font."""
    global FIGLET_AVAILABLE  # Add this line to access the global variable
    
    if FIGLET_AVAILABLE:
        try:
            fig = Figlet(font='standard')  # Changed from 'bitcount' to 'standard'
            banner_text = fig.renderText('TEMPORARY IDENTITY GENERATOR')
        except:
            # Fallback if 'standard' font is also not available
            FIGLET_AVAILABLE = False
            banner_text = "TEMPORARY IDENTITY GENERATOR"
    else:
        banner_text = "TEMPORARY IDENTITY GENERATOR"

    if FIGLET_AVAILABLE:
        # Split banner into lines and apply colors
        banner_lines = banner_text.split('\n')
        colored_banner = []
        colors = [fore.CYAN, fore.BLUE, fore.MAGENTA, fore.YELLOW, fore.GREEN, fore.CYAN] if COLORAMA_AVAILABLE else ['']
        for i, line in enumerate(banner_lines):
            if line.strip():
                color = colors[i % len(colors)] if COLORAMA_AVAILABLE else ''
                colored_banner.append(f"{color}{line}{fore.RESET if COLORAMA_AVAILABLE else ''}")
        banner = '\n'.join(colored_banner)
    else:
        # Fallback plain text banner
        banner = """
TEMPORARY IDENTITY GENERATOR
==========================
Temporary Identity Generator for Testing
"""

    print(banner)
    if COLORAMA_AVAILABLE:
        print(f"{style.BRIGHT}{fore.WHITE}by: MuyuG{style.RESET_ALL}")
        print(f"{fore.CYAN}github: https://github.com/Muyu-G{fore.RESET}")
    else:
        print("by: MuyuG")
        print("github: https://github.com/Muyu-G")