from dataclasses import dataclass

@dataclass
class UserCreateDto:
    user_id: str
    name: str
    username: str
    hashed_password: str # **在 DTO 中直接存 `hashed_password`**
    is_active: bool = True