from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class NextPhaseCommand(Command):
    def __init__(self, controller):
        self.controller = controller

    def execute(self):
        self.controller.next_phase()