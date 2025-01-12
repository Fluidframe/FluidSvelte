import os
import sys
import time
import subprocess
from typing import Optional


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



if __name__ == "__main__":
    # Allow running directly from command line
    if len(sys.argv) > 1:
        create_project(sys.argv[1])
    else:
        print("Please provide a project name")