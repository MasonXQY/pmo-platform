import os
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("AZURE_API_KEY")

if not KEY:
    raise ValueError("AZURE_API_KEY not found in environment")

# Kimi (Azure AI Foundry surface)
KIMI_URL = "https://internal-automation-swe-ai-res.services.ai.azure.com/openai/v1/chat/completions"

# Claude (Anthropic surface under openai.azure.com)
CLAUDE_URL = "https://internal-automation-swe-ai-res.openai.azure.com/anthropic/v1/messages"

# Azure GPT-5.2 (classic Azure OpenAI surface)
AZURE_GPT_URL = "https://anqi-mkqfvqs0-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-5.2-chat-2/chat/completions?api-version=2024-05-01-preview"
