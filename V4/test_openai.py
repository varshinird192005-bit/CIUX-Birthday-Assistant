
import os
from openai import OpenAI, APIStatusError

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

print("Testing OpenAI API connection...")

try:
    models = client.models.list()

    print("\nSUCCESS! API connection is working.")
    print("Available models:")

    for model in models.data:
        if "gpt-5.4-mini" in model.id:
            print("Found:", model.id)

except APIStatusError as error:

    print("\nAPI CONNECTION ERROR")
    print("Status:", error.status_code)
    print("Body:", repr(error.response.content))
    print("Headers:", dict(error.response.headers))

except Exception as error:

    print("\nOTHER ERROR")
    print(type(error).__name__)
    print(str(error))
