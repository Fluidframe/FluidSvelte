# FluidSvelte

![Fluidsvelte-logo](https://indigo-radical-heron-149.mypinata.cloud/ipfs/bafkreicg4yyrp252mj6z54gj5paebker5uf33kktlxzjsrqhywv2ya2dle)

FluidSvelte is an experimental Python-based full-stack web framework that unifies frontend and backend development using a component-based approach inspired by Svelte to extend developments of Fluidframe. It allows developers to write full-stack components in a single file using Python, HTML, CSS and optional Javascript/Typescript.


## Key Features
- Single-file components with Python, HTML, and CSS
- Fine-grained reactivity system similar to Svelte 5's runes
- Automatic compilation of components into Python backend and Svelte frontend code
- Seamless state synchronization between frontend and backend
- Type-safe communication using Protocol Buffers
- gRPC-based client-server communication


## Example Component
```fluid
<script lang="py">
count: int = State(0)

def increment():
    nonlocal count
    count += 1

def decrement():
    nonlocal count
    count -= 1

</script>

<button onclick={increment}>Increment</button>
<p>The count is: {count}</p>
<button onclick={decrement}>Decrement</button>

<style>
p {
    color: #ffffff;
    font-size: 1rem;
}
</style>
```

## How to try it out
1. Clone the library and install dependencies using astral uv with `uv sync`
2. create a `.fluid` file for example (currently only supports equivalent of `$state` rune from svelte as `State()` in python parallel with basic data types such as numbers, strings and booleans)
3. Try running `test.py` file by providing the `.fluid` component name and it will create a `dist/{component}/` folder with compiled `.py` and `.svelte` files.
4. `compiler.build()` will create an `app.py` backend server which binds the functional routes to the server
5. Run the generated app.py and use the generated `.svelte` component file within a svelte app as component (will later be combined together to be served completely from python itself)

    For creating a svelte app use `npm` and the following commands:
    1. `npm create vite@latest <project_name> -- --template svelte`
    2. `cd <project_name>`
    3. `npm install`
    4. Use the fluidsvelte compiler generated `.svelte` file of the component within `App.svelte` and run `npm run dev` as well as `uv run python app.py` running the fastapi backend and see it in action


Note: When creating reactive `State()` variables use python type annotation format `variable: annotation = State(default_value)` otherwise compilation won't include such variables.


## How It Works
1. Write components in `.fluid` files combining Python logic, HTML templates, and CSS styles
2. The Fluid compiler processes these files to generate:
  - Python backend code for business logic
  - Svelte frontend components for UI
  - Protocol Buffer definitions for type-safe communication (Not implemented yet)
3. Frontend interactions trigger gRPC calls to the backend (currently uses http post requests instead)
4. State updates are controlled by backend with python logic and state lives in frontend


## Technical Details
- Frontend: Svelte 5 with runes for reactivity
- Backend: Python with gRPC server
- Communication: Protocol Buffers and gRPC
- Component Compiler: Python AST-based parser and code generator


## Status
This project is currently in early experimental development. The core features being implemented are:
- Basic component compiler
- State management system
- gRPC communication layer (http communication layer currently)
- Code generation for Python and Svelte


## CLI commands:

`fluidsvelte init my-project`
```
my-project/                      # Root project directory
  ├── .fluidsvelte/              # Hidden directory for all framework internals
  │   ├── frontend/              # Compiled Svelte app
  │   ├── backend/               # Compiled Python backend
  │   ├── config/                # Framework configuration
  │   └── app.py                 # Compiled final fastapi App server
  │
  ├── src/                       # Main source folder for your application
  │   ├── lib/                   # Shared code (both Python & Svelte)
  │   │   ├── components/        # Reusable UI components
  │   │   │   ├── Header.fluid
  │   │   │   └── Footer.fluid
  │   │   │ 
  │   │   └── server/            # Server-side utilities
  │   │       └── db.py
  │   │
  │   ├── routes/                # All routes following SvelteKit conventions
  │   │   ├── +page.fluid        # Root page component
  │   │   ├── +layout.fluid      # Root layout
  │   │   ├── about/
  │   │   │   └── +page.fluid
  │   │   │
  │   │   └── blog/
  │   │       ├── +page.fluid
  │   │       └── +layout.fluid
  │   │
  │   ├── app.html               # Main HTML template for the application
  │   ├── error.html             # Custom error page template
  │   ├── app.py                 # Optional custom FastAPI server template (setup middlewares)
  │   └── app.config.py          # App configuration
  │
  ├── static/                    # Public assets
  │   ├── images/                
  │   └── styles/
  │
  ├── .gitignore    
  ├── .python-version    
  ├── pyproject.toml
  ├── README.md
  └── uv.lock                    
```


## Future Plans
Once stability is achieved, Fluidframe will follows this kind of application behaviour.
