from app.schemas.neo4j_schema import MemoryFacts, Entity, Relationship
import pytest

def test_memory_facts_valid():
    facts = MemoryFacts(
        store=True,
        reason="User mentioned a skill",
        entities=[Entity(name="Python", type="Technology", confidence=0.9)],
        relationships=[Relationship(source="User", relation="USES", target="Python", confidence=0.9)],
        facts=["User uses Python"]
    )
    assert facts.store == True
    assert len(facts.entities) == 1

def test_entity_confidence_out_of_range_is_rejected():
    # confidence must be between 0.0 and 1.0
    with pytest.raises(Exception):
        Entity(name="Python", type="Technology", confidence=1.5)  # > 1.0 is invalid
