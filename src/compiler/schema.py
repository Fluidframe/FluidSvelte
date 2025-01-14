import ast
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class ScriptSection:
    content: str
    lang:    str = "js"  # default to JavaScript
    AST:     Optional[ast.AST] = None


@dataclass
class ParsedSection:
    style:      Optional[str] = None
    scripts:    List[ScriptSection] = field(default_factory=list)
    template:   Optional[str] = None
    script_ast: Optional[ast.AST] = None  # Store Python AST specifically
    