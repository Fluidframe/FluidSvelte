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
<script type="python">
count: int = State(0)

def increment():
    count += 1

def decrement():
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


## How It Works
1. Write components in `.fluid` files combining Python logic, HTML templates, and CSS styles
2. The Fluid compiler processes these files to generate:
  - Python backend code for business logic
  - Svelte frontend components for UI
  - Protocol Buffer definitions for type-safe communication
3. Frontend interactions trigger gRPC calls to the backend
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
- gRPC communication layer
- Code generation for Python and Svelte


## Future Plans
Once stability is achieved, Fluidframe will follows this kind of application behaviour.
