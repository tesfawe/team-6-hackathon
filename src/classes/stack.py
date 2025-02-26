# Define the class that represents a stack of boxes
class StackOfBoxes:
    def __init__(self, camera_id: int, stack_height: int):
        self.camera_id = camera_id
        self.stack_height = stack_height
        self.is_safe = True  # Initially safe