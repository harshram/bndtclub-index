import os

def debug_print(message):
    '''
    It makes debug messages visibile on the console in case those are needed. 
    
    It leverages on the DEBUG environment variable: set to 'true' activates the debugging messages.
    '''
    # Read the DEBUG environment variable
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Print the message if debug mode is enabled
    if debug_mode:
        print(f"[DEBUG] {message}")

def info_print(message):
    '''
    It makes info messages visibile on the console in case those are needed.

    It leverages on the INFO environment variable: set to 'true' activates the debugging messages.
    '''
    # Read the DEBUG environment variable
    info_mode = os.getenv('DEBUG', 'False').lower() == 'true' or os.getenv('INFO', 'False').lower() == 'true'
    
    # Print the message if debug mode is enabled
    if info_mode:
        print(f"[INFO] {message}")

def error_print(message):
    '''
    It makes error messages visibile on the console
    '''
    print(f"[ERROR] {message}")