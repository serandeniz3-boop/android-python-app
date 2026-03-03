from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple, Any, Dict

@dataclass
class Quiz:
    q: str
    choices: List[str]
    answer: int
    explain: str = ""

@dataclass
class Lesson:
    id: str
    unit: int
    order: int
    title: str
    goal: str
    hint: str
    expected: str
    starter_code: str = ""
    input_example: str = ""
    expected_output_example: str = ""
    checks: List[Tuple[str, Callable[[Any], bool]]] = field(default_factory=list)
    intro: str = ""
    example: str = ""
    quiz: Optional[Dict[str, Any]] = None
