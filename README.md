# WelcomeBot

A Python project using DeepFace for facial recognition.

## Prerequisites

- Python 3.10-3.13
- Poetry

## Install

```bash
poetry install
```

## Usage

### Add a face to the database

```bash
poetry run python main.py add <name> <image_path_or_url>
```

### Find a face in the database

```bash
poetry run python main.py find <image_path_or_url>
```

**Note:** Both local file paths and HTTP(S) URLs are supported.
