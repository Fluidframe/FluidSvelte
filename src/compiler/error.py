class CompilationError(Exception):
    """Exception raised for errors during the Fluid compilation process."""
    def __init__(self, message: str, source: str = None, line_number: int = None):
        self.message = message
        self.source = source
        self.line_number = line_number
        
        # Build the error message
        error_msg = message
        if source and line_number:
            error_msg = f"{message}\nFile: {source}, Line: {line_number}"
        elif source:
            error_msg = f"{message}\nFile: {source}"
            
        super().__init__(error_msg)