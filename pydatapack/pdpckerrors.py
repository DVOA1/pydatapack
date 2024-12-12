class RecipeOutOfSlots(Exception):
    def __init__(self):
        self.message = "Too many ingredients! Maximum of 9 per shapless recipe (one per slot)"
        super().__init__(self.message)