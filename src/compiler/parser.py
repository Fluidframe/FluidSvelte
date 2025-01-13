import re, ast, os
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union, List


@dataclass
class ParsedSection:
    script: Optional[str] = None
    script_type: Optional[str] = None  # "python" or None for regular Svelte
    script_ast: Optional[ast.AST] = None
    template: Optional[str] = None
    style: Optional[str] = None


class TypeExtractor(ast.NodeVisitor):
    PROTO_TYPE_MAP = {
        'int': 'int32',
        'float': 'float',
        'str': 'string',
        'bool': 'bool',
        'bytes': 'bytes',
        'List': 'repeated',
        'Dict': 'map',
        'Any': 'google.protobuf.Any',
        'datetime': 'google.protobuf.Timestamp',
        'Decimal': 'string',
    }

    def get_proto_type(self, type_str: str) -> str:
        return self.PROTO_TYPE_MAP.get(type_str, type_str)

    def process_union_types(self, types: List[str]) -> List[str]:
        """Process and normalize union types"""
        return [self.get_proto_type(t.strip()) for t in types]

    def get_type_str(self, node) -> Union[str, List[str]]:
        if node is None:
            return "google.protobuf.Any"
            
        if isinstance(node, ast.Name):
            return self.get_proto_type(node.id)
            
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            # Handle type unions with | operator
            types = []
            current = node
            while isinstance(current, ast.BinOp) and isinstance(current.op, ast.BitOr):
                types.append(self.get_type_str(current.right))
                current = current.left
            types.append(self.get_type_str(current))
            return types
            
        elif isinstance(node, ast.Subscript):
            value = self.get_type_str(node.value)
            if isinstance(node.value, ast.Name) and node.value.id == 'Optional':
                slice_type = self.get_type_str(node.slice)
                if isinstance(slice_type, list):  # Optional[Union[...]]
                    return slice_type
                return [slice_type]
            return value

        return "google.protobuf.Any"


class FluidParser:
    def __init__(self):
        self.script_pattern = re.compile(
            r'<script(?:\s+lang="([^"]*)")?\s*>(.*?)</script>',
            re.DOTALL
        )
        self.style_pattern = re.compile(
            r'<style>(.*?)</style>',
            re.DOTALL
        )

    def parse_file(self, file_path: str) -> ParsedSection:
        with open(file_path, 'r') as f:
            content = f.read()
        
        parsed = ParsedSection()
        
        script_match = self.script_pattern.search(content)
        if script_match:
            script_type = script_match.group(1)
            script_content = script_match.group(2).strip()
            parsed.script = script_content
            parsed.script_type = script_type

            if script_type == "py":
                try:
                    parsed.script_ast = ast.parse(script_content)
                except SyntaxError as e:
                    raise ValueError(f"Invalid Python syntax in script: {e}")

        style_match = self.style_pattern.search(content)
        if style_match:
            parsed.style = style_match.group(1).strip()

        template = content
        template = self.script_pattern.sub('', template)
        template = self.style_pattern.sub('', template)
        parsed.template = template.strip()

        return parsed

    def extract_state_variables(self, ast_tree: ast.AST) -> List[Dict]:
        state_vars = []
        type_extractor = TypeExtractor()
        
        class StateVisitor(ast.NodeVisitor):
            def visit_AnnAssign(self, node):
                if (isinstance(node.value, ast.Call) and 
                    isinstance(node.value.func, ast.Name) and 
                    node.value.func.id == 'State'):
                    
                    type_info = type_extractor.get_type_str(node.annotation)
                    
                    # Handle initial value
                    initial_value = None
                    if node.value.args:
                        if isinstance(node.value.args[0], ast.Constant):
                            initial_value = node.value.args[0].value

                    state_info = {
                        'name': node.target.id,
                        'initial_value': initial_value,
                    }

                    # Handle union types vs simple types
                    if isinstance(type_info, list):
                        state_info['types'] = type_info
                        state_info['is_union'] = True
                    else:
                        state_info['type'] = type_info
                        state_info['is_union'] = False

                    state_vars.append(state_info)

        StateVisitor().visit(ast_tree)
        return state_vars

    def extract_functions(self, ast_tree: ast.AST) -> list:
        functions = []
        type_extractor = TypeExtractor()
        
        class FunctionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                params = []
                for arg in node.args.args:
                    param_info = {
                        'name': arg.arg,
                        'type': 'Any'
                    }
                    if arg.annotation:
                        param_info['type'] = type_extractor.get_type_str(arg.annotation)
                    params.append(param_info)

                return_type = 'None'
                if node.returns:
                    return_type = type_extractor.get_type_str(node.returns)

                functions.append({
                    'name': node.name,
                    'params': params,
                    'return_type': return_type,
                    'body': node.body,
                    'ast_node': node
                })

        FunctionVisitor().visit(ast_tree)
        return functions
    
    
if __name__ == "__main__":
    
    parser = FluidParser()
    parsed = parser.parse_file('counter.fluid')

    state_vars = parser.extract_state_variables(parsed.script_ast)
    functions = parser.extract_functions(parsed.script_ast)