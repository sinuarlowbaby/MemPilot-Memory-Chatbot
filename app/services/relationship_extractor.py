from litellm import acompletion
from app.prompts.memory_prompt import MEMORY_PROMPT
from app.schemas.neo4j_schema import MemoryFacts
import json
from langsmith import traceable

@traceable(run_type="llm", name="extract_relationships", metadata={"model":"gpt-4o-mini"})
async def extract_relationships(text:str):
    response = await acompletion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": MEMORY_PROMPT},
            {"role": "user", "content": "Extract relationships from the following text: " + text}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": MemoryFacts.model_json_schema()
        }
    )
    
    return json.loads(response.choices[0].message.content)