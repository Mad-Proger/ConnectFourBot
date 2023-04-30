import dataclasses


@dataclasses.dataclass
class Player:
    chat_id: int
    username: str
