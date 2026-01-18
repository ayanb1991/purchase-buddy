import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()
# Load credentials from environment variables
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")

if not all([azure_openai_api_key, azure_openai_endpoint, azure_openai_deployment]):
    raise EnvironmentError("Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME environment variables.")

# Initialize LangChain LLM with Azure OpenAI
llm = AzureChatOpenAI(
    openai_api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    deployment_name=azure_openai_deployment,
    openai_api_version=azure_openai_api_version,
    temperature=0
)

# Run a sample prompt
try:
    prompt = "What is the sum of 1 plus 1?"
    response = llm.invoke(prompt)
    print(f"Prompt: {prompt}")
    print(f"Connection successful! Response: {response.content}")
except Exception as e:
    print("Connection failed:", e)
