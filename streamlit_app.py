#!/usr/bin/env python3
"""
Streamlit Cloud Entry Point
This file serves as the main entry point for Streamlit Cloud deployment
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
import streamlit as st

# Redirect to the main app
if __name__ == "__main__":
    # Import the main app module
    from src.dashboard import app
