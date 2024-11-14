import os
from nemoguardrails import RailsConfig, LLMRails

# Load the OpenAI API key securely
OPENAI_KEY = os.getenv("OPENAI_KEY")
if not OPENAI_KEY:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_KEY environment variable.")

# Path to the config files that include CoLang rules
CONFIG_PATH = "/rails.co"

# Load Rails configuration
try:
    config = RailsConfig.from_path(CONFIG_PATH)
except Exception as e:
    raise ValueError(f"Could not load RailsConfig from '{CONFIG_PATH}': {e}")

# Initialize the LLMRails instance with the loaded configuration
rails = LLMRails(config, llm_api_key=OPENAI_KEY)

# Define a function to process user messages
def get_response(user_message: str) -> str:
    """Generates a response from the chatbot based on user input."""
    try:
        response = rails.generate(messages=[{
            "role": "user",
            "content": user_message
        }])
        if response and isinstance(response, list) and "content" in response[0]:
            return response[0]["content"]
    except Exception as e:
        return f"An error occurred while generating a response: {e}"
    return "Sorry, I couldn't generate a response."

# Example usage
if __name__ == "__main__":
    user_input = input("User: ")
    print("Chatbot:", get_response(user_input))
