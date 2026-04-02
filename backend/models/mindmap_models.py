from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MindmapNode(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    label: str = Field(..., description="The text content of the node (keep concise, 1-3 words)")
    level: int = Field(..., description="The hierarchical level (0 for root, 1 for main branches, 2 for subtopics)")
    parent_id: Optional[str] = Field(None, description="ID of the parent node (None for root)")
    children_ids: List[str] = Field(default_factory=list, description="List of child node IDs")

class MindmapStructure(BaseModel):
    nodes: List[MindmapNode] = Field(..., description="List of all nodes in the mindmap (maximum 3 levels)")
    root_id: str = Field(..., description="ID of the root/central node")
    title: str = Field(..., description="Title of the mindmap")
    description: Optional[str] = Field(None, description="Brief description of the mindmap content")

class SimpleMindmapStructure(BaseModel):
    """
    Simple hierarchical mindmap structure using Dict to avoid recursion issues.
    The structure will be validated as a nested dictionary with id, text, display, and nodes.

    Example:
    {
        "id": "root",
        "text": "Main Research Topic",
        "display": {"block": true},
        "nodes": [
            {
                "id": "1",
                "text": "Category A",
                "nodes": [
                    {
                        "id": "2",
                        "text": "Subtopic 1",
                        "nodes": []
                    }
                ]
            }
        ]
    }
    """
    mindmap: Dict[str, Any] = Field(..., description="Hierarchical mindmap structure with id, text, display, and nodes")
    title: str = Field(..., description="Title of the mindmap")
    description: Optional[str] = Field(None, description="Brief description of the mindmap content")