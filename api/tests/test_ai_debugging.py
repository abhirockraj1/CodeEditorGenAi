# tests/test_ai_debugging.py
import pytest
import httpx
import time
from typing import Dict, List 

BASE_URL = "http://127.0.0.1:8000/ai_debugging"  
ANALYZE_CODE_ENDPOINT = f"{BASE_URL}/analyze_code"

# --- Define necessary models
class CodeAnalysisRequest:
    def __init__(self, code: str, language: str):
        self.code = code
        self.language = language

class CodeAnalysisResponse:
    def __init__(self, suggestions: Dict[str, List[str]]):
        self.suggestions = suggestions

# --- Tests for /ai_debugging/analyze_code endpoint add timeout of 60seconds to each test case ---
def test_analyze_code_success():
    code = "def my_function(a, b):\n  return a + b"
    response = httpx.post(
        ANALYZE_CODE_ENDPOINT,
        json={"code": code, "language": "python"},
        timeout=60.0
    )
    assert response.status_code == 200
    assert "suggestions" in response.json()

def test_analyze_code_with_suggestions():
    code = "if a ="  # Simulate syntax error
    response = httpx.post(
        ANALYZE_CODE_ENDPOINT,
        json={"code": code, "language": "python"},
    )
    assert response.status_code == 200
    assert "syntax_errors" in response.json()["suggestions"]

def test_analyze_code_rate_limited():
    code = "print('hello')"
    for _ in range(5):
        response = httpx.post(
            ANALYZE_CODE_ENDPOINT,
            json={"code": code, "language": "python"},
        )
        assert response.status_code == 200

    response = httpx.post(
        ANALYZE_CODE_ENDPOINT,
        json={"code": code, "language": "python"},
    )
    assert response.status_code == 429
    assert "Too Many Requests" in response.text

def test_analyze_code_rate_limited_after_wait():
    code = "print('world')"
    for _ in range(5):
        response = httpx.post(
            ANALYZE_CODE_ENDPOINT,
            json={"code": code, "language": "python"},
        )
        assert response.status_code == 200

    time.sleep(65)

    response = httpx.post(
        ANALYZE_CODE_ENDPOINT,
        json={"code": code, "language": "python"},
    )
    assert response.status_code == 200
    assert "suggestions" in response.json()