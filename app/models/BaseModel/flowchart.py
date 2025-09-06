from pydantic import BaseModel
from typing import List, Optional

class Node(BaseModel):
    label: str
    children: Optional[List[int]] = None  # Recursive definition for child nodes

class Nodes(BaseModel):
    nodes: List[Node]

class flowchart_response(BaseModel):
    title: str
    flowchart: Nodes
    
class flowchart_request(BaseModel):
    text: str
    instruction: Optional[str] = None  # Optional instruction for flowchart generation
    userId: Optional[str] = None  # Optional user ID for personalization