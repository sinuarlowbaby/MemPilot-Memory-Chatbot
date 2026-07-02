from app.services.neo4j import make_strict_schema, extract_structured_knowledge, add_knowledge_to_graph, search_graph
from app.schemas.neo4j_schema import MemoryFacts, Entity, Relationship
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

def test_make_strict_schema_adds_additional_properties():
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    result = make_strict_schema(schema)
    assert result["additionalProperties"] == False

def test_make_strict_schema_adds_required():
    schema = {"type": "object", "properties": {"name": {}, "age": {}}}
    result = make_strict_schema(schema)
    assert set(result["required"]) == {"name", "age"}


@pytest.mark.asyncio
async def test_extract_structured_knowledge():
    """Verify that extract_structured_knowledge calls AsyncOpenAI.beta.chat.completions.parse correctly"""
    mock_facts = MemoryFacts(
        store=True,
        reason="test",
        entities=[Entity(name="A", type="Person", confidence=1.0)],
        relationships=[Relationship(source="A", relation="LIKES", target="B", confidence=1.0)],
        facts=["A likes B"]
    )
    
    with patch("app.services.neo4j.openai_client") as mock_openai:
        mock_openai.beta.chat.completions.parse = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(parsed=mock_facts))]
        ))
        
        result = await extract_structured_knowledge("A likes B")
        
        assert result.store is True
        assert len(result.entities) == 1
        assert result.entities[0].name == "A"
        mock_openai.beta.chat.completions.parse.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_knowledge_to_graph_no_store():
    """Verify add_knowledge_to_graph returns True and skips saving when store=False"""
    mock_facts = MemoryFacts(store=False, reason="no relation", entities=[], relationships=[], facts=[])
    
    with patch("app.services.neo4j.extract_structured_knowledge", new_callable=AsyncMock) as mock_extract, \
         patch("app.services.neo4j.neo4j_driver") as mock_driver:
        
        mock_extract.return_value = mock_facts
        result = await add_knowledge_to_graph("query", "response", "session123")
        
        assert result is True
        mock_driver.session.assert_not_called()


@pytest.mark.asyncio
async def test_add_knowledge_to_graph_success():
    """Verify add_knowledge_to_graph commits relationships to Neo4j driver when relationships exist"""
    mock_facts = MemoryFacts(
        store=True,
        reason="user works at google",
        entities=[
            Entity(name="User", type="Person", confidence=1.0),
            Entity(name="Google", type="Company", confidence=1.0)
        ],
        relationships=[
            Relationship(source="User", relation="WORKS_AT", target="Google", confidence=1.0)
        ],
        facts=["User works at Google"]
    )
    
    with patch("app.services.neo4j.extract_structured_knowledge", new_callable=AsyncMock) as mock_extract, \
         patch("app.services.neo4j.neo4j_driver") as mock_driver:
        
        mock_extract.return_value = mock_facts
        
        # Mock Neo4j session and transaction runners
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        result = await add_knowledge_to_graph("query", "response", "session123")
        
        assert result is True
        mock_session.run.assert_called_once()
        args, kwargs = mock_session.run.call_args
        assert "UNWIND $relationships AS rel" in args[0]
        assert kwargs["session_id"] == "session123"


@pytest.mark.asyncio
async def test_search_graph_queries_neo4j():
    """Verify search_graph queries Neo4j driver and formats returned relationship strings"""
    with patch("app.services.neo4j.neo4j_driver") as mock_driver:
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {"relationship": "User WORKS_AT Google"},
            {"relationship": "User LIKES Python"}
        ]
        
        result = await search_graph("User")
        
        assert "User WORKS_AT Google" in result
        assert "User LIKES Python" in result
        mock_session.run.assert_called_once()
