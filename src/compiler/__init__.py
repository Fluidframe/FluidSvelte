import os
from pathlib import Path
from typing import Union, List
from urllib.parse import urlparse
from src.compiler.parser import FluidParser
from src.compiler.error import CompilationError
from src.compiler.generator.python import PythonGenerator
from src.compiler.generator.svelte import SvelteGenerator


def extract_host_and_port(url: str):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    return host, port


class FluidCompiler:
    def __init__(self, base_url: str, output_dir: str = "dist"):
        self.components = []
        self.base_url = base_url
        self.parser = FluidParser()
        self.output_dir = output_dir
        
    def compile_files(self, file_paths: Union[str, List[str]]):
        """Compile multiple .fluid files
        
        Args:
            file_paths: Single file path or list of file paths to compile
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
            
        for file_path in file_paths:
            self.compile_file(file_path)

    def compile_directory(self, directory: str, recursive: bool = True):
        """Compile all .fluid files in a directory
        
        Args:
            directory: Directory path containing .fluid files
            recursive: If True, search subdirectories as well
        """
        pattern = "**/*.fluid" if recursive else "*.fluid"
        
        # Get all .fluid files in directory
        fluid_files = list(Path(directory).glob(pattern))
        
        if not fluid_files:
            raise CompilationError(f"No .fluid files found in {directory}")
            
        for fluid_file in fluid_files:
            try:
                self.compile_file(str(fluid_file))
            except Exception as e:
                print(f"Error compiling {fluid_file}: {str(e)}")
                continue

    def compile_file(self, file_path: str):
        try:
            component_name = os.path.splitext(os.path.basename(file_path))[0]
            parsed = self.parser.parse_file(file_path)
            
            # Check if we have a Python script
            has_python = any(script.lang == "py" for script in parsed.scripts)
            
            if has_python:
                state_vars = self.parser.extract_state_variables(parsed.script_ast)
                derived_vars = self.parser.extract_derived_variables(parsed.script_ast)
                functions = self.parser.extract_functions(parsed.script_ast)
                
                # Generate backend
                python_gen = PythonGenerator(component_name)
                python_code = python_gen.generate(parsed, state_vars, functions)
                
                # Generate frontend
                svelte_gen = SvelteGenerator(self.base_url, component_name)
                svelte_code = svelte_gen.generate(parsed, state_vars, derived_vars, functions)
                
                # Ensure output directory exists
                component_dir = os.path.join(self.output_dir, component_name)
                os.makedirs(component_dir, exist_ok=True)
                
                # Write files
                with open(os.path.join(component_dir, f"{component_name}.py"), "w") as f:
                    f.write(python_code)
                
                with open(os.path.join(component_dir, f"{component_name}.svelte"), "w") as f:
                    f.write(svelte_code)
                    
                self.components.append({
                    "name": component_name,
                    "import_path": f"from {self.output_dir}.{component_name}.{component_name} import router as {component_name}"
                })
            else:
                # Handle JavaScript-only components
                with open(os.path.join(self.output_dir, f"{component_name}.svelte"), "w") as f:
                    f.write(parsed.template)
        except Exception as e:
            raise CompilationError(
                "Failed to compile `.fluid` file",
                source=file_path,
            )

                
    def build(self):
        host, port = extract_host_and_port(self.base_url)
        route_imports="\n".join(
            [component['import_path'] for component in self.components]
        )
        include_routes="\n".join(
            [f"app.include_router({component['name']})" for component in self.components]
        )
        template = f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
{route_imports}

app = FastAPI()

{include_routes}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="{host}", port={port})
"""
        with open("app.py", "w") as f:
            f.write(template)
