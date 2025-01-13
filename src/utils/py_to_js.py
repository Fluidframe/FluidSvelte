import ast
from typing import List, Tuple


class PyToJSConverter:
    def __init__(self):
        self.operator_map = {
            'Add': '+',
            'Sub': '-',
            'Mult': '*',
            'Div': '/',
            'Mod': '%',
            'Pow': '^',
            'Gt': '>',
            'Lt': '<',
            'GtE': '>=',
            'LtE': '<=',
            'Eq': '=='
        }

    def parse_expression(self, node) -> str:
        if isinstance(node, ast.BinOp):
            left = self.parse_expression(node.left)
            right = self.parse_expression(node.right)
            op = self.operator_map.get(node.op.__class__.__name__, '')
            return f"({left} {op} {right})"
            
        elif isinstance(node, ast.Compare):
            left = self.parse_expression(node.left)
            right = self.parse_expression(node.comparators[0])
            op = self.operator_map.get(node.ops[0].__class__.__name__, '')
            return f"{left} {op} {right}"
            
        elif isinstance(node, ast.IfExp):
            test = self.parse_expression(node.test)
            body = self.parse_expression(node.body)
            orelse = self.parse_expression(node.orelse)
            return f"{test} ? {body} : {orelse}"
            
        elif isinstance(node, ast.Name):
            return node.id
            
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f'"{node.value}"'
            return str(node.value)
            
        elif isinstance(node, ast.List):
            elements = [self.parse_expression(elt) for elt in node.elts]
            return f"[{', '.join(elements)}]"
            
        elif isinstance(node, ast.Dict):
            pairs = []
            for key, value in zip(node.keys, node.values):
                if (isinstance(key, ast.Constant) and 
                    isinstance(key.value, str) and 
                    key.value.isidentifier()):
                    key_str = key.value
                else:
                    key_str = self.parse_expression(key)
                
                value_str = self.parse_expression(value)
                pairs.append(f"{key_str}: {value_str}")
            return f"{{{', '.join(pairs)}}}"
            
        elif isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant):
                    parts.append(str(value.value))
                elif isinstance(value, ast.FormattedValue):
                    expr = self.parse_expression(value.value)
                    parts.append(f"${{{expr}}}")
            return f"`{''.join(parts)}`"
            
        elif isinstance(node, ast.Tuple):
            elements = [self.parse_expression(elt) for elt in node.elts]
            return f"[{', '.join(elements)}]"
            
        elif isinstance(node, ast.Set):
            elements = [self.parse_expression(elt) for elt in node.elts]
            return f"new Set([{', '.join(elements)}])"
            
        return ""

    def convert_to_js(self, python_code: str) -> List[str]:
        tree = ast.parse(python_code)
        js_lines = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign):
                target = node.target.id
                value = node.value
                
                if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
                    func_name = value.func.id
                    
                    if func_name == 'State':
                        init_value = self.parse_expression(value.args[0]) if value.args else '0'
                        js_lines.append(f"let {target} = $state({init_value});")
                        
                    elif func_name == 'Derived':
                        expr = self.parse_expression(value.args[0])
                        js_lines.append(f"let {target} = $derived({expr});")
        
        return js_lines
    
    
if __name__ == "__main__":
    def convert_python_to_js(python_code: str) -> str:
        converter = PyToJSConverter()
        js_lines = converter.convert_to_js(python_code)
        return '\n'.join(js_lines)

    assert convert_python_to_js("""count: int = State(0)""") == "let count = $state(0);"
    assert convert_python_to_js("""root: float = State(0.0)""") == "let root = $state(0.0);"
    assert convert_python_to_js("""message: str = State("Hi hello")""") == """let message = $state("Hi hello");"""
    assert convert_python_to_js("""squared: str = Derived(f"Square of count {count} is {count * count}")""") == "let squared = $derived(`Square of count ${count} is ${(count * count)}`);"
    assert convert_python_to_js("""items: list = State(["apple", "banana", "orange"])""") == """let items = $state(["apple", "banana", "orange"]);"""
    assert convert_python_to_js("""config: dict = State({"name": message, "age": 30})""") == "let config = $state({name: message, age: 30});"
    assert convert_python_to_js("""numbers: tuple = State((1, 2, 3))""") == "let numbers = $state([1, 2, 3]);"
    assert convert_python_to_js("""unique_nums: set = State({1, 2, 3})""") == "let unique_nums = $state(new Set([1, 2, 3]));"
