from app.core.llm import get_llm_response

def generate_unit_test(chunk: dict) -> str:
    """
    Generates a unit test for a given function/class chunk.
    """
    language_hint = "pytest" if chunk["file"].endswith(".py") else "jest"

    prompt = f"""You are a senior QA engineer. Write a {language_hint} unit test for the following {chunk['type']} named '{chunk['name']}'.
Cover the main expected behavior and at least one edge case.
Only output the test code, no explanation.

CODE:
{chunk['code']}

UNIT TEST:"""

    return get_llm_response(prompt)