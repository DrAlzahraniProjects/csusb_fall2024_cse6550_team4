# Load the OpenAI API key securely
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Path to the config files that include CoLang rules
config_path = "./config"  

# Initialize the Rails configuration and load CoLang rules
config = RailsConfig.from_path(config_path)

# Initialize the LLMRails with the loaded configuration
rails = LLMRails(config, llm_api_key=OPENAI_KEY)

# Define a function to process user messages
def get_response(user_message):
    # Pass the message through NeMo Guardrails to get a response
    response = rails.generate(messages=[{
        "role": "user",
        "content": user_message
    }])
    
    # Print or return the response content
    return response[0]["content"]

# Example usage
if _name_ == "_main_":
    user_input = "Hello!"
    print("User:", user_input)
    print("Chatbot:", get_response(user_input))