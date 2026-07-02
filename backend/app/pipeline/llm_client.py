import requests
from app.config import LLM_URL


#*** FUNCTION TO CALLL THE LOCAL MISTRAL LLM
"""
    Sends a prompt to the local Mistral LLM and returns the response text.
    Uses requests.post() — no API key needed, just the URL.

    We try different JSON payload formats in case the server uses a different format.
    | Status Code | Meaning               |
| ----------- | --------------------- |
| 200         | OK (Success)          |
| 201         | Created               |
| 400         | Bad Request           |
| 401         | Unauthorized          |
| 403         | Forbidden             |
| 404         | Not Found             |
| 500         | Internal Server Error |
| 503         | Service Unavailable   |

"""

def call_llm(prompt_text, max_tokens=5000):
    headers={"Content-Type": "application/json"}  # tell the server that we are sending jon
    #This is payload formal for Mistral/Ollama-style local servers
    payload={
        "prompt":prompt_text,  # the full prompt text
        "max_tokens":max_tokens,  # limit response length
        "temperature":0.0  # zero randomness, Always choose the most likely next token. best for extraction tasks
    }

    try:
        response= requests.post(LLM_URL, headers=headers, json=payload, timeout=300)  # 2min timeout
        print("Status Code:", response.status_code)
        response.raise_for_status()  # Raise error if HTTP status is 4xx/5xx
        """If status is 200–299 → does nothing.
        If status is 4xx or 5xx → raises an exception."""

        result=response.json()  # parse the JSON response from server

         # Try common response field names used by different LLM servers
        if "response" in result:
            return result["response"]  # Ollama format
        elif "text" in result:
            return result["text"]  # Some custom servers
        elif "choices" in result:
            return result["choices"][0]["text"]  # Open-AI compatible format
        elif "generated_text" in result:
            return result["generated_text"]
        # If unknown format, print the raw response so you can adapt
        else:
            print("Unknow response format. Raw response:", result)

            #This is because the server response is a list containing one string, not a plain string.
            if isinstance(result, list) and len(result) > 0:
                return result[0]

            return str(result)

    except requests.exceptions.Timeout:
        print("Error: LLM request timed out after 120 seconds.")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to LLM. Check if the server is running.")
        return None
    except Exception as e:
        print(f"Error callling LLM: {e}")
        return None

print("call_llm function defined.")
