#!/usr/bin/env python3
"""
WelcomeBot - Face recognition using DeepFace
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from contextlib import contextmanager
import requests
from deepface import DeepFace


DB_PATH = "db"


def setup_db():
    """Create database directory if it doesn't exist"""
    Path(DB_PATH).mkdir(exist_ok=True)


@contextmanager
def get_image_path(image_path: str):
    """Get local path for image, downloading if it's a URL"""
    if image_path.startswith("http://") or image_path.startswith("https://"):
        print(f"Downloading image from {image_path}...")
        try:
            response = requests.get(image_path, timeout=30)
            response.raise_for_status()

            # Create temporary file with appropriate extension
            suffix = Path(image_path).suffix or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

            print("Download complete.")
            yield tmp_path

            # Clean up temporary file
            os.unlink(tmp_path)
        except Exception as e:
            print(f"Error downloading image: {e}")
            yield None
    else:
        yield image_path


def add_face(name: str, image_path: str):
    """Add a face to the database"""
    with get_image_path(image_path) as local_path:
        if local_path is None:
            return

        if not os.path.exists(local_path):
            print(f"Error: Image not found at {local_path}")
            return

        # Create person directory
        person_dir = Path(DB_PATH) / name
        person_dir.mkdir(exist_ok=True)

        # Copy image to database
        # For URLs, use a generic name; for local files, use original name
        if image_path.startswith("http://") or image_path.startswith("https://"):
            image_name = f"{name}_{len(list(person_dir.glob('*'))) + 1}{Path(local_path).suffix}"
        else:
            image_name = Path(image_path).name

        dest_path = person_dir / image_name
        shutil.copy2(local_path, dest_path)

        print(f"Added {image_name} to database for {name}")


def find_face(image_path: str):
    """Find a face in the database"""
    with get_image_path(image_path) as local_path:
        if local_path is None:
            return

        if not os.path.exists(local_path):
            print(f"Error: Image not found at {local_path}")
            return

        if not os.listdir(DB_PATH):
            print("Error: Database is empty. Add faces first using 'add' command.")
            return

        print(f"Searching for face...")

        try:
            results = DeepFace.find(img_path=local_path, db_path=DB_PATH)

            if len(results) > 0 and len(results[0]) > 0:
                print(f"\nFound {len(results[0])} match(es):")
                for idx, row in results[0].iterrows():
                    identity = row['identity']
                    distance = row['distance']
                    person_name = Path(identity).parent.name
                    print(f"  - {person_name} (distance: {distance:.4f})")
            else:
                print("No matches found in database.")
        except Exception as e:
            print(f"Error during search: {e}")


def main():
    setup_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add face:  python main.py add <name> <image_path>")
        print("  Find face: python main.py find <image_path>")
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) != 4:
            print("Usage: python main.py add <name> <image_path>")
            return
        name = sys.argv[2]
        image_path = sys.argv[3]
        add_face(name, image_path)

    elif command == "find":
        if len(sys.argv) != 3:
            print("Usage: python main.py find <image_path>")
            return
        image_path = sys.argv[2]
        find_face(image_path)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: add, find")


if __name__ == "__main__":
    main()
