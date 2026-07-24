from abc import ABC, abstractmethod


class InputManager(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_input(self):
        ...

    @abstractmethod
    def send_output(self):
        ...