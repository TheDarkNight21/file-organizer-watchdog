import os
import time
import logging
import shutil
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define directory paths
desktop_directory = "/Users/farisallaf/Desktop"
file_folder = "/Users/farisallaf/Desktop/files"
cpp_folder = "/Users/farisallaf/Desktop/c++"
py_folder = "/Users/farisallaf/Desktop/python"
java_folder = "/Users/farisallaf/Desktop/java"
downloads = "/Users/farisallaf/Downloads"
images_folder = "/Users/farisallaf/Desktop/images"
documents_folder = "/Users/farisallaf/Desktop/files"

def delayed_move(source, destination):
    """
    Move a file or folder from source to destination with a delay of 5 seconds.
    """
    def move_delay():
        shutil.move(source, destination)

    timer = threading.Timer(5, move_delay)
    timer.start()

def is_existing_file(filename, dir):
    """
    Determines if a folder with the same name already exists in the given directory.
    """
    with os.scandir(dir) as folder:
        for entries in folder:
            if entries.name == filename:
                return True
    return False

class MovingHandlerProg(FileSystemEventHandler):
    """
    Custom event handler for programming-related file movements.
    """
    def on_created(self, event):
        """
        Handle the on_created event for programming-related file movements.

        Moves files based on file extensions to designated folders.
        """
        try:
            with os.scandir(desktop_directory) as desktop:
                for folders in desktop:
                    if folders.is_dir():
                        with os.scandir(folders) as entries:
                            for entry in entries:
                                if entry.is_file():
                                    if entry.name == "CMakeLists.txt":
                                        delayed_move(folders.path, cpp_folder)
                                    elif entry.name.endswith(".py"):
                                        delayed_move(folders.path, py_folder)
                                    elif entry.name.endswith(".java"):
                                        delayed_move(folders.path, java_folder)
                                    else:
                                        continue
        except (OSError, IOError, shutil.Error) as e:
            logging.error(f"Error during file movement: {str(e)}")

class MovingHandlerDown(FileSystemEventHandler):
    """
    Custom event handler for downloads-related file movements.
    """
    def on_created(self, event):
        """
        Handle the on_created event for downloads-related file movements.

        Moves image files to the images folder and large PDF files to the file folder.
        """
        try:
            file_name = event.src_path.split("/")[-1]
            if file_name.endswith((".jpeg", ".jpg", ".png")):
                shutil.move(event.src_path, images_folder)
            elif file_name.endswith(".pdf") and (os.stat(event.src_path).st_size / (1024 * 1024) > 1):
                shutil.move(event.src_path, file_folder)
        except (OSError, IOError, shutil.Error) as e:
            logging.error(f"Error during file movement: {str(e)}")

if __name__ == "__main__":
    """
    Main script for monitoring and organizing files on the desktop and in the downloads folder.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set up the observer
    observer = Observer()

    # Set up event handlers
    code_handler = MovingHandlerProg()
    observer.schedule(code_handler, path=desktop_directory, recursive=True)
    
    down_handler = MovingHandlerDown()
    observer.schedule(down_handler, path=downloads, recursive=True)
    
    # Start the observer
    observer.start()

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the observer on keyboard interrupt
        observer.stop()

    # Wait for the observer to finish
    observer.join()
