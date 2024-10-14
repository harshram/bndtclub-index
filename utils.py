import os

import streamlit as st

print(">>> Env Variables")
print(st.secrets['VERBOSITY'])

def debug_print(message):
    '''
    It makes debug messages visibile on the console in case those are needed. 
    
    It leverages on the DEBUG environment variable: set to 'true' activates the debugging messages.
    '''
    # Print the message if debug mode is enabled
    if st.secrets['VERBOSITY'].lower() == 'debug':
        print(f"[DEBUG] {message}")

def info_print(message):
    '''
    It makes info messages visibile on the console in case those are needed.

    It leverages on the INFO environment variable: set to 'true' activates the debugging messages.
    '''
    # Print the message if debug mode is enabled
    if st.secrets['VERBOSITY'].lower() == 'debug' or st.secrets['VERBOSITY'].lower() == 'info':
        print(f"[INFO] {message}")

def error_print(message):
    '''
    It makes error messages visibile on the console
    '''
    print(f"[ERROR] {message}")