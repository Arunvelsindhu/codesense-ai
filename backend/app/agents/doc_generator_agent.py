from app.core.llm import get_llm_response

def generate_documentation(chunk: dict) -> str:
    """
    Takes a single code chunk and generates a docstring-style explanation.
    """
    prompt = f"""You are a senior software engineer writing documentation.
Explain what this {chunk['type']} named '{chunk['name']}' does.
Keep it clear and concise (3-5 sentences). Mention parameters and return value if relevant.

CODE:
{chunk['code']}

DOCUMENTATION:"""

    return get_llm_response(prompt)


def generate_readme(repo_name: str, chunks: list) -> str:
    """
    Generates a high-level README summary from all chunks in a repo.
    """
    summary_context = "\n".join(
        f"- {c['type']} '{c['name']}' in {c['file']} (lines {c['start_line']}-{c['end_line']})"
        for c in chunks[:50]  # limit context size
    )

    prompt = f"""You are a technical writer. Based on this list of functions/classes found in the repo '{repo_name}', write a concise README.md style overview covering:
1. What the project likely does
2. Its main components/modules
3. How the pieces likely fit together

COMPONENTS FOUND:
{summary_context}

README:"""

    return get_llm_response(prompt)
def explain_code_snippet(code: str, language: str = "auto") -> str:
    """
    Explains an arbitrary pasted code snippet, no repo required.
    """
    prompt = f"""You are a senior software engineer explaining code to another developer.
Explain what this code does in plain language. Cover:
1. Overall purpose
2. Key logic / how it works step by step
3. Any parameters, inputs, or return values
4. Anything notable (edge cases, potential issues) if relevant

Language hint: {language}

CODE:
{code}

EXPLANATION:"""

    return get_llm_response(prompt)