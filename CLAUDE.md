# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python command-line utility that calculates MD5 checksums of files and returns them as Base64-encoded strings. The implementation processes files in 8192-byte chunks for efficient memory usage.

## Architecture

The application consists of a single Python file (`main.py`) with two main functions:

- `compute_checksum(file_path: str) -> Optional[str]`: Calculates MD5 checksum and returns Base64-encoded result
- `main()`: Handles command-line arguments and orchestrates the checksum calculation

## Common Commands

### Running the Application

```bash
python3 main.py <file_path>
```

### Environment Management

```bash
# Install dependencies (currently none beyond stdlib)
pipenv install

# Activate virtual environment
pipenv shell

# Run with pipenv
pipenv run python3 main.py <file_path>
```

### Development

This project uses Python 3.12.2 and pipenv for dependency management. The application currently has no external dependencies beyond Python's standard library.

## Key Implementation Details

- Uses MD5 hashing algorithm with Base64 encoding output
- Processes files in 8192-byte chunks
- Handles file reading errors gracefully
- Command-line interface expects exactly one argument (file path)
- Returns exit code 1 on errors, 0 on success
