from math import ceil

from bearlibterminal import terminal


class MessageLog:
    def __init__(self):
        self.messages = []

        self.padding_left: int = 1
        self.padding_right: int = 1
        self.padding_top: int = 40
        self.padding_bottom: int = 0
        self.mouse_scroll_step: int = 2

        self.frame_offset: int = 0
        self.frame_width: int = 0
        self.frame_height: int = 0
        self.total_messages_height: int = 1
        self.scrollbar_height: int = 0
        self.dragging_scrollbar_offset: int = 0

    def to_json(self):
        json_data = {
            'messages': self.messages
        }

        return json_data

    @classmethod
    def from_json(cls, json_data):
        message_log = cls()

        messages = json_data['messages']

        for message in messages:
            message_log.add_message(message)

        return message_log

    def add_message(self, message: str):
        self.messages.append(message)

        if self.scrollbar_height > 0:
            self.scroll_down()

    def render(self):
        if not self.messages:
            return

        self.update_geometry()

        terminal.layer = 0
        terminal.clear_area(self.padding_left, self.padding_top, self.frame_width, self.frame_height)

        index: int = 0
        first_line: int = 0

        while index < self.total_messages_height:
            message = self.messages[index]
            _, message_height = terminal.measuref(message)

            if first_line + message_height >= self.frame_offset:
                break

            first_line += message_height + 1

            index += 1

        delta: int = int(first_line - self.frame_offset)

        terminal.layer = 1

        while index < len(self.messages) and delta <= self.frame_height:
            message = self.messages[index]

            terminal.puts(self.padding_left, self.padding_top + delta, message, self.frame_width, 0,
                          terminal.state(terminal.TK_ALIGN_DEFAULT))

            _, message_height = terminal.measuref(message)
            delta += message_height
            index += 1

        terminal.layer = 0
        terminal.clear_area(self.padding_left + self.frame_width, self.padding_top, 1, self.frame_height)

        scrollbar_column: int = self.padding_left + self.frame_width
        scrollbar_offset = (self.padding_top + (self.frame_height - self.scrollbar_height) * (self.frame_offset / self.total_messages_height)) * terminal.state(terminal.TK_CELL_HEIGHT)

        for i in range(self.scrollbar_height):
            terminal.put_ext(scrollbar_column, i, 0, int(scrollbar_offset), 0x2588)

    def reset(self):
        self.messages = []
        self.frame_offset = 0

    def scroll_down(self):
        self.scroll_to_pixel(terminal.TK_CELL_HEIGHT * terminal.TK_HEIGHT)

    def scroll_to_pixel(self, pixel_y: int):
        pixel_y -= self.padding_top * terminal.state(terminal.TK_CELL_HEIGHT)
        factor = pixel_y / (self.frame_height * terminal.state(terminal.TK_CELL_HEIGHT))
        self.frame_offset = self.total_messages_height * factor
        self.frame_offset = max(0, min(self.total_messages_height - self.frame_height, self.frame_offset))

    def update_geometry(self):
        current_offset_percentage = self.frame_offset / self.total_messages_height

        self.frame_width = terminal.state(terminal.TK_WIDTH) - (self.padding_left + self.padding_right + 1)
        self.frame_height = terminal.state(terminal.TK_HEIGHT) - (self.padding_top + self.padding_bottom)

        self.total_messages_height = self.update_heights()

        self.scrollbar_height = min(ceil(self.frame_height * (self.frame_height / self.total_messages_height)),
                                    self.frame_height)

        self.frame_offset = self.total_messages_height * current_offset_percentage
        self.frame_offset = min(self.frame_offset, self.total_messages_height - self.frame_height)

        if self.total_messages_height <= self.frame_height:
            self.frame_offset = 0

    def update_heights(self):
        total_height: int = 0

        for message in self.messages:
            _, message_height = terminal.measuref(message)
            total_height += message_height

        total_height += len(self.messages) - 1

        return total_height
