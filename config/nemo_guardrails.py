import os
from nemoguardrails import RailsConfig
from nemoguardrails import LLMRails

OPENAI_KEY = os.getenv("OPENAI_KEY")

config = RailsConfig.from_path("./config")

rails = LLMRails(config)

response = rails.generate(messages=[{
    "role": "user",
    "content": "Hello!"
}])