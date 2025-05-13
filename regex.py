from __future__ import annotations


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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


class AsciiState(State):
    def __init__(self, *, state: State | None = None, char: str = ""):
        if char == "":
            raise ValueError("char cannot be empty")

        super().__init__(state=state, char=char)

    def check_self(self, char: str) -> State:
        if self.char == char:
            return self.next
        return EliminationState()


class DotState(State):
    def check_self(self, char: str) -> State:
        return self.next


class StarState(State):
    def __init__(self, *, state: State | None = None, char: str = ""):
        if state is TerminationState() or state is EliminationState():
            raise ValueError("invalid state")

        super().__init__(state=state, char=char)

    def check_self(self, char: str) -> State:
        if self.next.check_self(char) is not EliminationState():
            return self

        return self.next.next


class PlusState(State):
    def __init__(self, *, state: State | None = None, char: str = ""):
        if state is TerminationState() or state is EliminationState():
            raise ValueError("invalid state")

        super().__init__(state=state, char=char)

    def check_self(self, char: str) -> State:
        if self.next.check_self(char) is not EliminationState():
            return StarState(state=self.next, char=self.char)

        return EliminationState()


class TerminationState(State, metaclass=Singleton): ...


class EliminationState(State, metaclass=Singleton): ...


class RegexFSM:
    def __init__(self, regex_pattern: str):
        if regex_pattern == "":
            raise ValueError("Invalid regex")

        self.state: State = TerminationState()
        i = len(regex_pattern) - 1
        while i >= 0:
            self.state, i = self.__init_state(regex_pattern, i)

        self.start_state = self.state

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

    def __get_out_of_star(self) -> None:
        if isinstance(self.state, StarState):
            self.state = self.state.next.next
            self.__get_out_of_star()


if __name__ == "__main__":
    regex_pattern = "aa+"

    regex_compiled = RegexFSM(regex_pattern)
    assert regex_compiled.check_string("aa") == True
    assert regex_compiled.check_string("a") == False

    regex_compiled = RegexFSM("a*b+")
    assert regex_compiled.check_string("abbbbbb") == True
    assert regex_compiled.check_string("") == False

    regex_compiled = RegexFSM("a*+")
    assert regex_compiled.check_string("ab") == False

    regex_compiled = RegexFSM("a*")
    assert regex_compiled.check_string("") == True
