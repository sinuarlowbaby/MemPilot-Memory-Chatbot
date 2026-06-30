# app/tests/test_neo4j_conn.py
import pytest
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def test_neo4j_connection():
    """Integration test: verifies Neo4j is reachable"""
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URL"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    )
    with driver.session() as session:
        result = session.run("RETURN 1 AS value")
        record = result.single()
        assert record["value"] == 1  # ← pytest will catch this properly
    driver.close()
