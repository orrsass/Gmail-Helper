from dataclasses import dataclass
from typing import Optional

@dataclass
class Email:
    subject: str
    sender: str
    category: Optional[str] = None
    priority: Optional[int] = None
    action_required: bool = False 