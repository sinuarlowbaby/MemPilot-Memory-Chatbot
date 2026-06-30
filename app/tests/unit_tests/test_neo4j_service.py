from app.services.neo4j import make_strict_schema

def test_make_strict_schema_adds_additional_properties():
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    result = make_strict_schema(schema)
    assert result["additionalProperties"] == False

def test_make_strict_schema_adds_required():
    schema = {"type": "object", "properties": {"name": {}, "age": {}}}
    result = make_strict_schema(schema)
    assert set(result["required"]) == {"name", "age"}
