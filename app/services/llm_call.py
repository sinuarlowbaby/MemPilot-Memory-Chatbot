from litellm import acompletion

async def call_llm(user_query, relevent_memories,graph_relations, session_id, model):
    system_instruction = (
        "You are an intelligent, helpful assistant. You have access to a hybrid memory system "
        "comprising two sources:\n"
        "1. Semantic Memories (unstructured/vector memory): General context, qualitative preferences, "
        "and descriptive information about the user.\n"
        "2. Graph Relationships (structured graph database): Precise entities (e.g., people, projects, "
        "technologies) and the exact relationships between them.\n\n"
        "Guidelines:\n"
        "- Synthesize information from both memory sources to answer the user query accurately.\n"
        "- Rely on the structured Graph Relationships for factual accuracy regarding entities and their connections.\n"
        "- Maintain a natural, conversational tone. Do not explicitly reference terms like 'Semantic Memories', "
        "'Graph Relationships', or 'database' in your final response unless the user asks how your memory is implemented.\n"
        "- If the memories are empty or irrelevant, answer using your general knowledge naturally."
    )

    user_content = (
        f"User Query: {user_query}\n\n"
        f"--- Retrospective Context ---\n"
        f"Semantic Memories:\n{relevent_memories}\n\n"
        f"Graph Relationships:\n{graph_relations}"
    )
    
    # 3. Get response from LLM using system and user messages
    response = await acompletion(
        model=model,
        temperature=0.1,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ]
    )
    
    return response.choices[0].message.content