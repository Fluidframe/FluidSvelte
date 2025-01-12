from src.compiler import FluidCompiler
from src.utils.file_utils import create_project

compiler = FluidCompiler(
    output_dir="dist",
    base_url="http://127.0.0.1:8000",
)
compiler.compile_file("examples/counter2.fluid")
compiler.build()

create_project("fluidsvelte")