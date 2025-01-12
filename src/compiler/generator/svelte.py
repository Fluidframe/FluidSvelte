import ast
from typing import List, Dict

class SvelteGenerator:
    def __init__(self, base_url: str, component_name: str):
        self.base_url = base_url
        self.component_name = component_name

    def _generate_state_declarations(self, state_vars: List[Dict]) -> str:
        declarations = []
        for state in state_vars:
            initial_value = state['initial_value']
            if isinstance(initial_value, str):
                initial_value = f"'{initial_value}'"
            elif initial_value is None:
                initial_value = "null"  # Convert Python None to JavaScript null
            declarations.append(f"  let {state['name']} = $state({initial_value});")
        return '\n'.join(declarations)

    def _extract_nonlocals(self, func_node: ast.AST) -> List[str]:
        nonlocals = []
        for node in ast.walk(func_node):
            if isinstance(node, ast.Nonlocal):
                nonlocals.extend(node.names)
        return nonlocals

    def _generate_function(self, func_info: Dict, state_vars: List[Dict]) -> str:
        # Get nonlocal variables to determine which states are used/modified
        used_states = self._extract_nonlocals(func_info['ast_node'])
        
        # Generate the request payload
        state_params = ", ".join(f"{state}: {state}" for state in used_states)
        
        # Generate state updates from response
        state_updates = '\n    '.join(f"{state} = data.{state};" for state in used_states)
        
        return f"""
  async function {func_info['name']}() {{
    const response = await fetch('{self.base_url}/{self.component_name}/{func_info['name']}', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ {state_params} }})
    }});
    const data = await response.json();
    {state_updates}
  }}"""

    def generate(self, parsed_content, state_vars: List[Dict], functions: List[Dict]) -> str:
        script = f"""<script>
{self._generate_state_declarations(state_vars)}

{chr(10).join(self._generate_function(func, state_vars) for func in functions)}
</script>

{parsed_content.template}

<style>
{parsed_content.style}
</style>"""
        return script