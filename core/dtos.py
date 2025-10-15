from dataclasses import dataclass

@dataclass
class UserCreateDto:
    user_id: str
    name: str
    username: str
    password: str # 仍是明文，但仅用于传输到 service