from typing import List, Dict
import ast

class PythonGenerator:
    def __init__(self, component_name: str):
        self.component_name = component_name

    def _generate_imports(self) -> str:
        return """from fastapi import Request, APIRouter

router = APIRouter(prefix="/{}")
""".format(self.component_name)

    def _extract_nonlocals(self, func_node: ast.AST) -> List[str]:
        nonlocals = []
        for node in ast.walk(func_node):
            if isinstance(node, ast.Nonlocal):
                nonlocals.extend(node.names)
        return nonlocals

    def _generate_function(self, func_info: Dict, state_vars: List[Dict]) -> str:
        # Get nonlocal variables used in this function
        nonlocals = self._extract_nonlocals(func_info['ast_node'])
        
        # Get state declarations for all nonlocal variables
        state_declarations = [
            f"    {var} = data.get('{var}')"
            for var in nonlocals
        ]

        # Get the original function's content
        original_func = ast.unparse(func_info['ast_node'])
        # Indent the function definition
        indented_func = '\n'.join(f"    {line}" for line in original_func.split('\n'))

        return f"""
@router.post("/{func_info['name']}")
async def {func_info['name']}(request: Request):
    data = await request.json()
{chr(10).join(state_declarations)}
{indented_func}
    {func_info['name']}()
    return {{{', '.join(f"'{var}': {var}" for var in nonlocals)}}}
"""

    def generate(self, parsed_content, state_vars: List[Dict], functions: List[Dict]) -> str:
        code = [self._generate_imports()]
        code.extend(self._generate_function(func, state_vars) for func in functions)
        return '\n'.join(code)