import os
from urllib.parse import urlparse
from src.compiler.parser import FluidParser
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

    def compile_file(self, file_path: str):
        # Get component name from file name
        component_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Parse the fluid file
        parsed = self.parser.parse_file(file_path)
        
        if parsed.script_type == "py":
            # Extract state and functions
            state_vars = self.parser.extract_state_variables(parsed.script_ast)
            functions = self.parser.extract_functions(parsed.script_ast)
            
            # Generate Python backend
            python_gen = PythonGenerator(component_name)
            python_code = python_gen.generate(parsed, state_vars, functions)
            
            # Generate Svelte frontend
            svelte_gen = SvelteGenerator(self.base_url, component_name)
            svelte_code = svelte_gen.generate(parsed, state_vars, functions)
            
            # Create output directory
            os.makedirs(f"{self.output_dir}/{component_name}", exist_ok=True)
            
            # Write files
            with open(f"{self.output_dir}/{component_name}/{component_name}.py", "w") as f:
                f.write(python_code)
            
            with open(f"{self.output_dir}/{component_name}/{component_name}.svelte", "w") as f:
                f.write(svelte_code)
            
            self.components.append({"name": component_name, "import_path": f"from {self.output_dir}.{component_name}.{component_name} import router as {component_name}"})
        else:
            # If not Python, just create Svelte file
            with open(f"{self.output_dir}/{component_name}.svelte", "w") as f:
                f.write(parsed.script + parsed.template + parsed.style)
                
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
