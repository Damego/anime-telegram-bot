class VarChar:
    def __init__(self, max_chars: int):
        self.max_chars: int = max_chars

    def __str__(self):
        return f"VARCHAR({self.max_chars})"
