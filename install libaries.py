import subprocess
import sys

# List of libraries to install
libraries = [
    "flask",
    "mysql-connector-python",
    "requests",
]

# Function to install a library
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install each library
for lib in libraries:
    try:
        print(f"Installing {lib}...")
        install(lib)
        print(f"{lib} installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {lib}. Error: {e}")

# Optional: Install tkinter if not on Windows or MacOS
if sys.platform.startswith("linux"):
    try:
        print("Installing tkinter...")
        subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3-tk"])
        print("tkinter installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install tkinter. Error: {e}")
