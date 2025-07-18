#!/usr/bin/env python3

import base64
import hashlib
import os
import sys
import tempfile
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional

# Constants
CHUNK_SIZE = 8192
MAX_MEMORY_SIZE = 1 * 1024 * 1024  # 1MB in bytes


def is_url(path: str) -> bool:
    """Check if the given path is a URL."""
    parsed = urllib.parse.urlparse(path)
    return parsed.scheme in ('http', 'https')


def get_remote_file_size(url: str) -> Optional[int]:
    """Get the size of a remote file using HEAD request."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req) as response:
            content_length = response.headers.get('Content-Length')
            if content_length:
                return int(content_length)
            return None
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
        print(f"Error: Cannot get file size from '{url}': {e}")
        return None
    except Exception as e:
        print(f"Error: Unexpected error checking file size: {e}")
        return None


def compute_checksum_from_memory(url: str) -> Optional[str]:
    """Download file to memory and compute checksum for small files."""
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()

        md5_hash = hashlib.md5(data)
        digest = md5_hash.digest()
        checksum = base64.b64encode(digest).decode('utf-8')
        return checksum
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"Error: Cannot download file from '{url}': {e}")
        return None
    except MemoryError:
        print(f"Error: File too large to process in memory")
        return None
    except Exception as e:
        print(f"Error: Unexpected error processing URL '{url}': {e}")
        return None


def compute_checksum_from_download(url: str) -> Optional[str]:
    """Download large file to temporary file and compute checksum."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

            with urllib.request.urlopen(url) as response:
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    temp_file.write(chunk)

        checksum = compute_checksum(temp_path)
        return checksum
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"Error: Cannot download file from '{url}': {e}")
        return None
    except OSError as e:
        print(f"Error: Cannot create temporary file: {e}")
        return None
    except Exception as e:
        print(f"Error: Unexpected error downloading '{url}': {e}")
        return None
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def compute_checksum(file_path: str) -> Optional[str]:
    """
    Calculate MD5 checksum of a file and return Base64-encoded result.
    """
    try:
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            # Read in chunks for efficient memory usage
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
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
    except OSError as e:
        print(f"Error: OS error accessing file '{file_path}': {e}")
        return None
    except Exception as e:
        print(f"Error: Unexpected error processing file '{file_path}': {e}")
        return None


def main():
    """Main function to handle command line arguments and compute file checksum."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <file_path_or_url>")
        sys.exit(1)

    path_or_url = sys.argv[1]

    if is_url(path_or_url):
        # Handle URL
        file_size = get_remote_file_size(path_or_url)

        if file_size is None:
            # Cannot determine size, try in-memory first with fallback to temp file
            print(
                "Warning: Cannot determine file size, attempting in-memory processing with fallback...")
            checksum = compute_checksum_from_memory(path_or_url)
            if checksum is None:
                # If in-memory failed (likely due to size), fallback to temp file approach
                print(
                    "In-memory processing failed, falling back to temporary file download...")
                checksum = compute_checksum_from_download(path_or_url)
        elif file_size < MAX_MEMORY_SIZE:
            # Small file - process in memory
            print(f"File size: {file_size} bytes (processing in memory)")
            checksum = compute_checksum_from_memory(path_or_url)
        else:
            # Large file - download to temp file
            print(
                f"File size: {file_size} bytes (downloading to temporary file)")
            checksum = compute_checksum_from_download(path_or_url)
    else:
        # Handle local file
        checksum = compute_checksum(path_or_url)

    if checksum:
        print(f"Checksum: {checksum}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
