FluidSvelte is a full-stack web application framework that combines Python backend logic with Svelte's frontend capabilities in a unified component format. The project is inspired by several frameworks and approaches:

1. Svelte 5's runes for fine-grained reactivity
2. Streamlit's unified frontend-backend approach
3. Single File Components from Vue/Svelte
4. Python's server-side capabilities

Core Features:
- Custom .fluid file format that allows mixing Python and JavaScript code
- State management using `State()` similar to Svelte 5's $state(). (**Note: `State()` is not a function nor a class but is used for the compiler to identify reactive states to match with `$state` rune**) 
- Automatic API endpoint generation from Python functions
- Seamless state synchronization between frontend and backend
- Support for both Python backend logic and JavaScript frontend features

File Structure:
```fluid
<script lang="py">
  # Python backend logic with State declarations
  count: int = State(0)
  
  def increment():
      nonlocal count
      count += 1
</script>

<script lang="js">
    console.log(count);
  // Frontend-specific JavaScript code
  // Can use browser APIs and JS libraries
</script>

<!-- Template section -->
<button onclick={increment}>Increment</button>

<style>
  /* CSS styles */
</style>`
```

Compilation Process:

1. Parser extracts different sections from .fluid files
2. Generates Python backend code with FastAPI endpoints
3. Creates Svelte components with API integration
4. Maintains state synchronization through HTTP endpoints

Generated Output:
1. Python Backend (filename/filename.py):

```python
from fastapi import Request, APIRouter

router = APIRouter(prefix="/<filename>")

@router.post("/increment")
async def increment(request: Request):
    data = await request.json()
    count = data.get("count")
    def increment():
        nonlocal count
        count += 1
    increment()
    return {"count": count}
```

2. Svelte Frontend (filename/filename.svelte):

```svelte
<script>
let count = $state(0);

async function increment() {
    const response = await fetch('/counter/increment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count })
    });
    const data = await response.json();
    count = data.count;
}

console.log(count);
// Rest of the original JavaScript code preserved
</script>
```

Current Implementation:
- Basic parser for .fluid files
- Python and JavaScript code extraction
- FastAPI endpoint generation
- Svelte component generation with state management


Project Structure:
```
FluidSvelte/
├── src/
│   ├── compiler/
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   └── generator/
│   │       ├── __init__.py
│   │       ├── python.py
│   │       └── svelte.py
│   ├── runtime/
│   └── utils/
│       ├── __init__.py
│       └── file_utils.py
├── examples/
└── tests/
```


Current Focus:
1. Stable core compilation pipeline
2. Basic state management support of `$state` rune
3. FastAPI integration
4. Svelte component generation
5. Support for other svelte runes like `$derived`

The project aims to provide a seamless development experience where developers can write both backend and frontend logic in a single file while leveraging the best features of both Python and JavaScript ecosystems.
