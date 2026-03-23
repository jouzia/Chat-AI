import sys
import os


# Add the root directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard.app import main

if __name__ == "__main__":
    main()
