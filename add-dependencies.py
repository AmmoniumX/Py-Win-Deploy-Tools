import os
import sys
import zipfile
import tempfile
import os
import subprocess
import argparse
import urllib.request
import shutil
import glob
from pathlib import Path
from typing import TypeAlias

PathLike: TypeAlias = str | bytes | os.PathLike

def add_dependencies(get_pip_path: PathLike, embed_path: PathLike, requirements_path: PathLike, output_path: PathLike, delete_temp_dir: bool = True) -> None:
    """
    Extract embedded Python zip, enable pip, install packages, and repackage.
    
    Args:
        get_pip_path: Path to the get-pip.py script
        embed_path: Path to the embedded Python zip file
        requirements_path: Path to the requirements.txt file
        output_path: Path to save the modified embedded Python zip file
        delete_temp_dir = True: Whether to delete the temporary directory after processing
    """
    print(f"Processing embedded Python zip: {embed_path}")
    print(f"Installing dependencies from: {requirements_path}")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory(dir='.', delete=delete_temp_dir) as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Extract the embedded Python zip
        print("Extracting embedded Python zip...")
        with zipfile.ZipFile(embed_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the Python executable in the extracted files
        python_exe = os.path.join(temp_dir, "python.exe")
        if not os.path.exists(python_exe):
            # Try to find it in a subdirectory
            for root, _dirs, files in os.walk(temp_dir):
                if "python.exe" in files:
                    python_exe = os.path.join(root, "python.exe")
                    break
        
        print(f"Using Python executable: {python_exe}")
        
        # Enable pip by modifying _pth file
        pth_files = glob.glob(os.path.join(temp_dir, "python*._pth"))
        if pth_files:
            pth_file = pth_files[0]  # Use the first match
            print(f"Found _pth file: {pth_file}")
            print(f"Enabling import system in {pth_file}...")
            with open(pth_file, 'a') as f:
                f.write("\nimport site\n")
        else:
            raise RuntimeError(f"No Python _pth file found in {temp_dir}")
        
        # Create necessary directories
        site_packages_dir = os.path.join(temp_dir, "Lib", "site-packages")
        os.makedirs(site_packages_dir, exist_ok=True)
        
        # Install pip
        command = [python_exe, get_pip_path, "--no-warn-script-location"]
        print("Installing pip...", *command)
        subprocess.run(command, check=True)
        
        # Install requirements
        print(f"Installing packages from {requirements_path}...")
        pip_path = os.path.join(temp_dir, "Scripts", "pip.exe")
        if os.path.exists(pip_path):
            command = [pip_path, "install", "--no-warn-script-location", "-r", str(requirements_path)]
            print("Installing packages...", *command)
            subprocess.run(command, check=True)
        else:
            raise RuntimeError(f"pip executable not found: {pip_path}")
        # Create a new zip file
        print(f"Creating new zip file: {output_path}")
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Modified embedded Python zip created successfully: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add dependencies to an embedded Python zip file.")
    parser.add_argument("get_pip_path", type=str, help="Path to the get-pip.py script")
    parser.add_argument("embed_path", type=str, help="Path to the embedded Python zip file")
    parser.add_argument("requirements_path", type=str, help="Path to the requirements.txt file")
    parser.add_argument("output_path", type=str, help="Path to save the modified embedded Python zip file")
    parser.add_argument("--no-delete-temp-dir", dest="delete_temp_dir", action="store_false", help="Do not delete the temporary directory after processing")
    args = parser.parse_args()

    embed_path = Path(args.embed_path).resolve()
    get_pip_path = Path(args.get_pip_path).resolve()
    requirements_path = Path(args.requirements_path).resolve()
    output_path = Path(args.output_path).resolve()
    delete_temp_dir = args.delete_temp_dir

    if not embed_path.exists():
        raise RuntimeError(f"Embedded Python zip file does not exist: {embed_path}")
    if not requirements_path.exists():
        raise RuntimeError(f"Requirements file does not exist: {requirements_path}")
    if output_path.exists():
        raise RuntimeError(f"Output file already exists: {output_path}")
    
    add_dependencies(get_pip_path, embed_path, requirements_path, output_path, delete_temp_dir=delete_temp_dir)
    sys.exit(0)

    
