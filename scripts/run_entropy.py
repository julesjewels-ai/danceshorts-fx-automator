#!/usr/bin/env python3
import sys
import os

# Add src to path so we can import entropy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from entropy.main import main

if __name__ == "__main__":
    main()
