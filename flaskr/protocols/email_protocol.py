from typing import Protocol


class EmailModelProtocol(Protocol):
    def __init__(self, subject: str, body: str, sender_username: str, recipient_username: str):
        ...

    def is_valid(self) -> bool:
        ...