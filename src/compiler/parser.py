import re, ast, os
from dataclasses import dataclass
from src.compiler.converter import PyToJSConverter
from typing import Optional, Dict, Any, Union, List
from src.compiler.schema import ParsedSection, ScriptSection


class TypeExtractor(ast.NodeVisitor):
    def get_type_str(self, node) -> Union[str, List[str]]:
        if node is None:
            return "any"
            
        if isinstance(node, ast.Name):
            return node.id
            
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
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
                return slice_type if isinstance(slice_type, list) else [slice_type]
            return value

        return "any"


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
        parsed = ParsedSection()
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract all sections
            for script_match in self.script_pattern.finditer(content):
                lang = script_match.group(1) or "js"
                script_content = script_match.group(2).strip()
                
                script_section = ScriptSection(content=script_content, lang=lang)
                
                if lang == "py":
                    try:
                        script_section.AST = ast.parse(script_content)
                        # Store Python AST specifically
                        parsed.script_ast = script_section.AST
                    except SyntaxError as e:
                        raise ValueError(f"Invalid Python syntax: {e}")
                
                parsed.scripts.append(script_section)
            
            # Extract style and template
            if style_match := self.style_pattern.search(content):
                parsed.style = style_match.group(1).strip()
            
            # Extract template last to avoid interference
            template = content
            template = self.script_pattern.sub('', template)
            template = self.style_pattern.sub('', template)
            parsed.template = template.strip()
            
            return parsed
        except Exception as e:
            raise ValueError(f"Failed to parse {file_path}: {str(e)}")

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
    
    def extract_derived_variables(self, ast_tree: ast.AST) -> List[Dict]:
        derived_vars = []
        js_converter = PyToJSConverter()
        
        for node in ast.walk(ast_tree):
            if (isinstance(node, ast.AnnAssign) and 
                isinstance(node.value, ast.Call) and
                isinstance(node.value.func, ast.Name) and 
                node.value.func.id == 'Derived'):
                
                derived_vars.append({
                    'name': node.target.id,
                    'expression': js_converter.parse_expression(node.value.args[0])
                })
        return derived_vars

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
