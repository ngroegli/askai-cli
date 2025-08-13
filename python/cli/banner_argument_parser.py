"""
Custom argument parser module that displays an ASCII banner.
Extends the standard argparse.ArgumentParser with banner display functionality.
"""

import sys
import argparse
from termcolor import colored

def print_ascii_banner():
    """Print a stylized ASCII art banner for the application in cyan color."""
    banner_color = "cyan"
    banner = r'''
      ___         ___         ___         ___               
     /\  \       /\  \       /\__\       /\  \        ___   
    /::\  \     /::\  \     /:/  /      /::\  \      /\  \  
   /:/\:\  \   /:/\ \  \   /:/__/      /:/\:\  \     \:\  \ 
  /::\~\:\  \ _\:\~\ \  \ /::\__\____ /::\~\:\  \    /::\__\ 
 /:/\:\ \:\__/\ \:\ \ \__/:/\:::::\__/:/\:\ \:\__\__/:/\/__/ 
 \/__\:\/:/  \:\ \:\ \/__\/_|:|~~|~  \/__\:\/:/  /\/:/  /   
      \::/  / \:\ \:\__\    |:|  |        \::/  /\::/__/    
      /:/  /   \:\/:/  /    |:|  |        /:/  /  \:\__\    
     /:/  /     \::/  /     |:|  |       /:/  /    \/__/    
     \/__/       \/__/       \|__|       \/__/              
'''

    print(colored(banner, banner_color))


class BannerArgumentParser(argparse.ArgumentParser):
    """
    Custom argument parser that displays an ASCII banner.
    
    Extends the standard ArgumentParser with improved error handling and
    automatic banner display when showing help information.
    """
    def error(self, message):
        """
        Override error method to display errors in red and exit.
        
        Args:
            message: The error message to display
        """
        print(colored(f"ERROR: {message}", "red"))
        sys.exit(2)

    def print_help(self, *args, **kwargs):
        """
        Override print_help to display the ASCII banner before the help text.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        print_ascii_banner()
        super().print_help(*args, **kwargs)
