from dataclasses import dataclass
from objects import Process


@dataclass()
class General(Process):
    """
    General process which stores global system requirements etc.
    """
    name: str = "General"
    short_label: str = "Gen"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self):
        pass
