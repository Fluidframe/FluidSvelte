from src.compiler import FluidCompiler

compiler = FluidCompiler(
    output_dir="dist",
    base_url="http://127.0.0.1:8000",
)
compiler.compile_file("examples/counter2.fluid")
compiler.build()
