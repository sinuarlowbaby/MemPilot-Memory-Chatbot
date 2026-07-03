from litellm import acompletion

async def call_llm(user_query, relevent_memories, session_id, model):
    # 2. Build the prompt
    prompt = f"""
        You are a helpful assistant. You are given a user query and a list of relevant memories.
        Use the memories to answer the user query.

        User Query: {user_query}
        Relevant Memories: {relevent_memories}

        Answer: 
        """
    
    # 3. Get response from OpenAI
    response = await acompletion(
        model=model,
        temperature=0.1,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content