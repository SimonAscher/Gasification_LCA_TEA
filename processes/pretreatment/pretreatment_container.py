from dataclasses import dataclass
from objects import Process


@dataclass()
class Pretreatment(Process):
    name: str = "Pretreatment"
    short_label: str = "Pre."

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self):
        pass
