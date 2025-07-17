#!/usr/bin/env python3

import base64
import hashlib
import os
import sys
from typing import Optional


def compute_checksum(file_path: str) -> Optional[str]:
    """
    Calculate MD5 checksum of a file and return Base64-encoded result.
    """
    try:
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            # Read in chunks of 8192 bytes
            for chunk in iter(lambda: f.read(8192), b''):
                md5_hash.update(chunk)

        # Get the digest and encode to Base64 without line wrapping
        digest = md5_hash.digest()
        checksum = base64.b64encode(digest).decode('utf-8')
        return checksum
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except PermissionError:
        print(f"Error: Permission denied accessing file '{file_path}'")
        return None
    except IsADirectoryError:
        print(f"Error: '{file_path}' is a directory, not a file")
        return None
    except IOError as e:
        print(f"Error: I/O error reading file '{file_path}': {e}")
        return None
    except OSError as e:
        print(f"Error: OS error accessing file '{file_path}': {e}")
        return None
    except Exception as e:
        print(f"Error: Unexpected error processing file '{file_path}': {e}")
        return None


def main():
    """Main function to handle command line arguments and compute file checksum."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)

    checksum = compute_checksum(file_path)
    if checksum:
        print(f"Checksum: {checksum}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
