from typing import TypeVar, Generic, Any, Optional


T = TypeVar('T')


class State(Generic[T]):
    def __init__(self, initial_value: T):
        self._value = initial_value

    def __repr__(self) -> str:
        return repr(self._value)

    def __str__(self) -> str:
        return str(self._value)

    # Numeric operations
    def __add__(self, other):
        return self._value + (other._value if isinstance(other, State) else other)

    def __sub__(self, other):
        return self._value - (other._value if isinstance(other, State) else other)

    def __mul__(self, other):
        return self._value * (other._value if isinstance(other, State) else other)

    def __truediv__(self, other):
        return self._value / (other._value if isinstance(other, State) else other)

    def __floordiv__(self, other):
        return self._value // (other._value if isinstance(other, State) else other)

    # Reverse operations
    def __radd__(self, other):
        return other + self._value

    def __rsub__(self, other):
        return other - self._value

    def __rmul__(self, other):
        return other * self._value

    def __rtruediv__(self, other):
        return other / self._value

    # Augmented assignments
    def __iadd__(self, other):
        self._value += (other._value if isinstance(other, State) else other)
        return self

    def __isub__(self, other):
        self._value -= (other._value if isinstance(other, State) else other)
        return self

    def __imul__(self, other):
        self._value *= (other._value if isinstance(other, State) else other)
        return self

    def __itruediv__(self, other):
        self._value /= (other._value if isinstance(other, State) else other)
        return self

    # Comparison operations
    def __eq__(self, other):
        return self._value == (other._value if isinstance(other, State) else other)

    def __lt__(self, other):
        return self._value < (other._value if isinstance(other, State) else other)

    def __le__(self, other):
        return self._value <= (other._value if isinstance(other, State) else other)

    def __gt__(self, other):
        return self._value > (other._value if isinstance(other, State) else other)

    def __ge__(self, other):
        return self._value >= (other._value if isinstance(other, State) else other)

    # Value access
    def __get__(self, obj, objtype=None):
        return self._value

    def __set__(self, obj, value):
        self._value = value

    # For direct value access when using the variable
    def __call__(self):
        return self._value

    # Allow direct assignment
    def __setattr__(self, name, value):
        if name == '_value':
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)
            
            

def test_state():
    # Basic initialization and value access
    count = State(0)
    assert count==0
    
    # Addition
    count += 1
    assert count==1

    # Direct assignment
    count = 42
    assert count==42

    # None assignment
    count = None
    assert count is None

    # String state
    text = State("hello")
    text += " world"
    assert text=="hello world"

    # Float operations
    number = State(5.5)
    number *= 2
    assert number==11.0

    # Comparisons
    x = State(10)
    y = State(20)
    assert (x < y) == True
    assert (x == 10) == True

if __name__ == "__main__":
    test_state()

