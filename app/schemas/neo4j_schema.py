from pydantic import BaseModel, Field
from typing import List

class Entity(BaseModel):
    name: str = Field(..., description="Entity name")
    type: str = Field(
        ...,
        description="Entity type such as Person, Technology, Project, Company, Goal, Skill, Language, Database, Framework"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the entity extraction (0.0 - 1.0)"
    )


class Relationship(BaseModel):
    source: str = Field(..., description="Source entity")
    relation: str = Field(
        ...,
        description="Relationship type such as USES, WORKS_ON, LIKES, LEARNS, CREATED, PREFERS"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the relationship extraction (0.0 - 1.0)"
    )
    target: str = Field(..., description="Target entity")


class MemoryFacts(BaseModel):
    store: bool = Field(..., description="Whether this conversation contains long-term memory")
    reason: str = Field(..., description="Reason for storing memory")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    relationships: List[Relationship] = Field(default_factory=list, description="Relationships between entities")
    facts: List[str] = Field(default_factory=list, description="Human-readable memory facts")