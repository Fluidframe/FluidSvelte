import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict


def create_project(project_name: str) -> bool:
    """
    Creates a new Svelte 5 project using Vite.
    
    Args:
        project_name: The name of the project to create
        
    Returns:
        bool: True if project was created successfully, False otherwise
    """
    try:
        if not project_name.isalnum() and '-' not in project_name:
            raise ValueError("Project name must contain only letters, numbers, or hyphens")
        
        if os.path.exists(project_name):
            raise FileExistsError(f"Directory '{project_name}' already exists")
            
        print(f"Creating new Svelte 5 project: {project_name}")
        
        # Create project using npm create vite
        subprocess.run([
            "npm",
            "create",
            "vite@latest",
            project_name,
            "--",
            "--template",
            "svelte"
        ], check=True)
        
        os.chdir(project_name)
        
        print("Installing dependencies...")
        subprocess.run(["npm", "install"], check=True)
        
        print(f"\nSuccess! Created FluidSvelte project '{project_name}'")
        # print("\nTo get started:")
        # print(f"  cd {project_name}")
        # print("  npm run dev")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False
    except Exception as e:
        print(f"Error creating project: {e}")
        return False


###########################################################################################


def create_directory_structure(project_path: Path, directories: List[str]) -> None:
    """
    Creates the directory structure inside the project folder.
    
    Args:
        project_path: The project root path
        directories: List of directories to create
    """
    for directory in directories:
        dir_path = project_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)

def create_empty_files(project_path: Path, files: List[str]) -> None:
    """
    Creates empty files in the project structure.
    
    Args:
        project_path: The project root path
        files: List of files to create
    """
    for file_path in files:
        (project_path / file_path).touch()

def setup_fluidsvelte(project_path: Path, fluidsvelte_dir: str) -> bool:
    """
    Sets up the Fluidsvelte framework directory using npm.
    
    Args:
        project_path: The project root path
        fluidsvelte_dir: The directory name for fluidsvelte
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        # Create Fluidsvelte framework
        subprocess.run([
            "npm",
            "create",
            "vite@latest",
            fluidsvelte_dir,
            "--",
            "--template",
            "svelte"
        ], check=True, cwd=project_path)

        # Change directory to Fluidsvelte folder and run npm install
        fluidsvelte_path = project_path / fluidsvelte_dir
        subprocess.run(["npm", "install"], check=True, cwd=fluidsvelte_path)

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

def setup_dependencies(project_path: Path, project_name: str) -> None:
    try:
        subprocess.run(["uv", "init"], check=True, cwd=project_path)
        subprocess.run(["uv", "sync"], check=True, cwd=project_path)
        subprocess.run(["uv", "add", "fastapi"], check=True, cwd=project_path)
        subprocess.run(["uv", "add", "uvicorn"], check=True, cwd=project_path)
        return True
    except subprocess.CalledProcessError:
        return False

def init_project(
    project_name: str,
    source_dir: str = "src",
    static_dir: str = "assets",
    fluidsvelte_dir: str = "fluidsvelte"
) -> bool:
    """
    Initializes a new FluidSvelte 5 project.
    
    Args:
        project_name: The name of the project to initialize
        source_dir: The directory to keep application source files
        static_dir: The directory to keep static files
        fluidsvelte_dir: The directory to keep fluidsvelte specific files
        
    Returns:
        bool: True if the project was successfully initialized, False otherwise.
    """
    try:
        # Create the project directory in current working directory
        cwd = Path.cwd()
        project_path = cwd / project_name
        
        # Check if project directory already exists
        if project_path.exists():
            print(f"Error: Directory '{project_name}' already exists")
            return False
            
        # Create the project root directory
        project_path.mkdir(parents=True)
        
        # Define directory structure
        directories = [
            f"{source_dir}/lib/components",
            f"{source_dir}/lib/server",
            f"{source_dir}/routes",
            f"{static_dir}/images",
            f"{static_dir}/styles",
        ]
        
        # Define files to create
        files = [
            f"{source_dir}/app.py",
            f"{source_dir}/app.fluid",
            f"{source_dir}/error.fluid",
            f"{source_dir}/fluidsvelte_config.py",
            f"{source_dir}/routes/+page.fluid",
            f"{source_dir}/lib/components/Header.fluid",
            f"{source_dir}/lib/components/Footer.fluid",
        ]
        
        # Create directories and files
        create_directory_structure(project_path, directories)
        create_empty_files(project_path, files)
        
        # Setup Fluidsvelte framework
        if not setup_fluidsvelte(project_path, fluidsvelte_dir):
            print("Error: Failed to setup Fluidsvelte framework")
            shutil.rmtree(project_path)
            return False
        
        # Create configuration files
        setup_dependencies(project_path, project_name)
        
        print(f"\nProject '{project_name}' created successfully!")
        print("\nTo get started:")
        print(f"  cd {project_name}")
        print("  pip install -e .")
        print(f"  cd {fluidsvelte_dir} && npm install")
        print("  npm run dev")
        
        return True
        
    except Exception as e:
        print(f"Error initializing project: {str(e)}")
        # Clean up if something went wrong
        if project_path.exists():
            shutil.rmtree(project_path)
        return False


if __name__ == "__main__":
    if project_name := input("Enter project name: ").strip():
        init_project(project_name)