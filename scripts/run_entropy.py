#!/usr/bin/env python3
import sys
import os

# Ensure src is in python path
sys.path.append(os.getcwd())

from src.entropy.manager import EntropyManager

def main():
    try:
        manager = EntropyManager()
        manager.run()
    except Exception as e:
        print(f"Entropy execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
