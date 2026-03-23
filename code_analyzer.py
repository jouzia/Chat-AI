import os
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from vector_store import get_vector_store
from typing import Any
def analyze_python_code(code: str) -> dict[str, Any]:
    """
    Static analysis using Python's built-in AST module.
    Extracts classes, functions, imports and produces a structural overview.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}"}

    classes: list[str] = []
    functions: list[str] = []
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            else:
                imports.append(node.module or "")

    return {
        "classes": classes,
        "functions": functions,
        "imports": imports,
        "summary": (
            f"Found {len(classes)} class(es), {len(functions)} function(s), "
            f"and {len(imports)} import(s)."
        ),
    }


def get_llm_code_review(code: str, llm=None) -> str:
    """
    Request a code review from the LLM.
    Pass a LangChain chat model as `llm`; falls back to a placeholder message
    so the app stays functional without credentials.
    """
    if llm is None:
        return (
            "No LLM available for deep review. "
            "Initialize a model via get_llm() in assistant.py and pass it here."
        )

    prompt = (
        "You are an expert Python code reviewer. "
        "Review the code below and provide:\n"
        "1. Bugs or logical errors\n"
        "2. Security issues\n"
        "3. Performance improvements\n"
        "4. Missing type hints or docstrings\n\n"
        f"```python\n{code}\n```"
    )
    response = llm.invoke(prompt)
    return response.content
