import os
import sys
from dotenv import load_dotenv

# Ensure app path is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

try:
    print("Testing connection to Neo4j and Qdrant...")
    from app.services.mem0_service import memory
    
    # Try adding a test memory to see if the graph db stores it
    print("Adding a test memory to trigger Neo4j and Qdrant writes...")
    memory.add("John lives in Boston.", user_id="test_user_123")
    
    print("Retrieving memories to verify...")
    res = memory.search("Where does John live?", filters={"user_id": "test_user_123"})
    print("Search Result:", res)
    
    print("✅ Connection is SUCCESSFUL! Both Qdrant and Neo4j are connected.")
except Exception as e:
    print("❌ Connection FAILED!")
    import traceback
    traceback.print_exc()
