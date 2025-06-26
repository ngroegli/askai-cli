import argparse
from termcolor import colored

def print_ascii_banner():
    banner_color = "cyan"
    banner = '''
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
    def print_help(self, *args, **kwargs):
        print_ascii_banner()
        super().print_help(*args, **kwargs)
