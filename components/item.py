class Item:
    def __init__(self, use_function=None, targeting: bool = False, targeting_message: str = None, **kwargs):
        self.use_function = use_function
        self.targeting: bool = targeting
        self.targeting_message: str = targeting_message
        self.function_kwargs = kwargs
