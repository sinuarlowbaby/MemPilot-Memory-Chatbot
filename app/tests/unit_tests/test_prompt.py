from app.prompts.memory_prompt import MEMORY_PROMPT

def test_memory_prompt_exists():
    assert MEMORY_PROMPT is not None
    assert len(MEMORY_PROMPT) > 0

def test_memory_prompt_is_string():
    assert isinstance(MEMORY_PROMPT, str)

def test_memory_prompt_contains_keywords():
    # These keywords are actually in memory_prompt.py
    assert "DO NOT store" in MEMORY_PROMPT
    assert "JSON" in MEMORY_PROMPT
    assert "Extract" in MEMORY_PROMPT
    assert "long-term" in MEMORY_PROMPT
    assert "greetings" in MEMORY_PROMPT

    