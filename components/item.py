import item_functions


class Item:
    def __init__(self, use_function=None, targeting: bool = False, targeting_message: str = None, **kwargs):
        self.use_function = use_function
        self.targeting: bool = targeting
        self.targeting_message: str = targeting_message
        self.function_kwargs = kwargs

    def to_json(self):
        json_data = {
            'targeting': self.targeting,
            'targeting_message': self.targeting_message,
            'function_kwargs': self.function_kwargs
        }

        if self.use_function:
            json_data['use_function_name'] = self.use_function.__name__
        else:
            json_data['use_function_name'] = None

        return json_data

    @classmethod
    def from_json(cls, json_data):
        use_function_name = json_data.get('use_function_name')
        targeting = json_data.get('targeting', False)
        targeting_message = json_data.get('targeting_message', '')
        function_kwargs = json_data.get('function_kwargs', {})

        if use_function_name:
            use_function = getattr(item_functions, use_function_name)
        else:
            use_function = None

        item = cls(
            use_function=use_function,
            targeting=targeting,
            targeting_message=targeting_message,
            **function_kwargs
        )

        return item
