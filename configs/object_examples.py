from requirement_objects import Electricity, Heat, Requirements
from process_objects import Process
from dataclasses import dataclass

# Example process object workflow

# Test requirement objects
elect_object = Electricity(values=[10, 10], name="Aux demands")
heat_object = Heat(values=[30, 20])
requirements1 = Requirements(name="Test1")
requirements1.add_requirement(elect_object)
requirements1.add_requirement(elect_object)
requirements1.add_requirement(heat_object)

requirements2 = Requirements(name="Test2")
requirements2.add_requirement(elect_object)

# Test process objects

# Create new process object


@dataclass()
class NewProcess(Process):
    name: str = "Example process"
    instantiate_with_default_reqs = False

    def instantiate_default_requirements(self):
        pass


process_A = NewProcess(name="Example process", instantiate_with_default_reqs=False)
# subprocess_of_process_A = NewProcess(name="subprocess of A", instantiate_with_default_reqs=False)
# process_A.add_subprocess(subprocess_of_process_A)
process_A.add_requirements(requirements1)
# process_A.add_requirements(requirements2)
process_A.calculate_GWP()
# TODO: See why this error occurs here but not in e.g. gasification model
