# discrete_lab_3

## Usage
To use RegexFSM you need to construct RegexFSM object and pass the regex expression.
Then you can use check_string method to check if the string matches the compiled regex.

## Explanation

### RegexFSM
In \_\_init\_\_ it complies the regex in a while loop and forms a linkeked list from states:
```python
    def __init__(self, regex_pattern: str):
        if regex_pattern == "":
            raise ValueError("Invalid regex")

        self.state: State = TerminationState()
        i = len(regex_pattern) - 1
        while i >= 0:
            self.state, i = self.__init_state(regex_pattern, i)

        self.start_state = self.state
```


At the start i points to the last element of the expression
then in \_\_init\_state it matches the symbol, that i points to:
```python
    def __init_state(self, regex_pattern: str, i: int) -> tuple[State, int]:
        char = regex_pattern[i]

        if char == "*":
            new_state, j = self.__init_state(regex_pattern, i - 1)
            return StarState(state=new_state), j
        if char == ".":
            return DotState(char=char, state=self.state), i - 1
        if char == "+":
            new_state, j = self.__init_state(regex_pattern, i - 1)
            return PlusState(state=new_state), j
        if char.isascii():
            return AsciiState(char=char, state=self.state), i - 1
        raise ValueError("Invalid regex")
```
When the state depends on the next state, it gets it recursively.

## States:
I have 6 State classes: AsciiState, StarState, DotState, PlusState, TerminationState, EliminationState,
which all inherit from State base class:
```python
class State:
    def __init__(self, *, state: State | None = None, char: str = ""):
        if isinstance(self, (TerminationState, EliminationState)):
            return

        if state is None:
            self.next: State = TerminationState()
        else:
            self.next: State = state

        self.char: str = char

    def check_self(self, char: str) -> State:
        return EliminationState()
```

\_\_init\_\_ accepts 2 positional:
char - current regex expression character
state - the next state (reading expression backwards), TerminationState if not specified

check_self function checks the current character and returns the next state to check

### AsciiState
```python
class AsciiState(State):
    def __init__(self, *, state: State | None = None, char: str = ""):
        if char == "":
            raise ValueError("char cannot be empty")

        super().__init__(state=state, char=char)

    def check_self(self, char: str) -> State:
        if self.char == char:
            return self.next
        return EliminationState()
```
AsciiState saves the letter, when initialized and when the check_self method is called
it checks if char is equal to the saved one.
if it is, the function returns the next state, if not - EliminationState

### DotState
```python
class DotState(State):
    def check_self(self, char: str) -> State:
        return self.next
```
it just returns the next state

### StarState
in init you need to pass the "inner" state, which it would check for

```python
class StarState(State):
    def __init__(self, *, state: State | None = None, char: str = ""):
        if state is TerminationState() or state is EliminationState():
            raise ValueError("invalid state")

        super().__init__(state=state, char=char)

    def check_self(self, char: str) -> State:
        if self.next.check_self(char) is not EliminationState():
            return self

        return self.next.next
```
it returns itself while the return state from "inner" state is not EliminationState
then it skips over the "inner" state and returns the next one

### PlusState
If the first time it check the "inner" state returns EliminationState, it propagates it further,
If not, it the StartState with the same init parameters

```python
class PlusState(State):
    def __init__(self, *, state: State | None = None, char: str = ""):
        if state is TerminationState() or state is EliminationState():
            raise ValueError("invalid state")

        super().__init__(state=state, char=char)

    def check_self(self, char: str) -> State:
        if self.next.check_self(char) is not EliminationState():
            return StarState(state=self.next, char=self.char)

        return EliminationState()
```

## check_string
for every character in text, checks if current state is not the elimination state

```python
    def check_string(self, text: str) -> bool:
        self.state = self.start_state
        for char in text:
            self.state = self.state.check_self(char)
            if self.state is EliminationState():
                return False

        self.__get_out_of_star()

        if self.state is TerminationState():
            return True
        return False
```

## uitility functions and classes

At the end of the cycle if the last state was a StarState it persists, so we need to get rid of them
```python
def __get_out_of_star(self) -> None:
        if isinstance(self.state, StarState):
            self.state = self.state.next.next
            self.__get_out_of_star()
```

The Singleton metaclass is used by TerminationState and EliminationState to make sure that the exists only
one instance of each class in teh process
```python
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
```
