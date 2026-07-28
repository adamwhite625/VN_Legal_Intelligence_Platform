"""
Minimal test script for AWS Bedrock LLM - no database or Redis required.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Read credentials directly from environment
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "openai.gpt-oss-120b-1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "ap-northeast-1")
AWS_BEARER_TOKEN = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

print("=" * 50)
print("Bedrock Connection Test")
print("=" * 50)
print(f"LLM_PROVIDER     : {LLM_PROVIDER}")
print(f"BEDROCK_MODEL_ID : {BEDROCK_MODEL_ID}")
print(f"BEDROCK_REGION   : {BEDROCK_REGION}")
print(f"Bearer Token Set : {'Yes' if AWS_BEARER_TOKEN else 'No - check .env'}")
print("=" * 50)

if LLM_PROVIDER != "bedrock":
    print("LLM_PROVIDER is not 'bedrock'. Set LLM_PROVIDER=bedrock in .env to test Bedrock.")
    sys.exit(1)

if not AWS_BEARER_TOKEN:
    print("AWS_BEARER_TOKEN_BEDROCK is not set in .env")
    sys.exit(1)

os.environ["AWS_BEARER_TOKEN_BEDROCK"] = AWS_BEARER_TOKEN

try:
    from langchain_aws import ChatBedrockConverse
    print("\nInitializing ChatBedrockConverse...")

    llm = ChatBedrockConverse(
        model=BEDROCK_MODEL_ID,
        region_name=BEDROCK_REGION,
        temperature=TEMPERATURE,
    )
    print(f"LLM Class: {llm.__class__.__name__}")

    print("\nSending test prompt...")
    response = llm.invoke("Trả lời ngắn gọn: Bạn là AI gì và đang chạy trên nền tảng nào?")
    content = getattr(response, "content", str(response))

    print("\nModel Response:")
    print("-" * 50)
    print(content)
    print("-" * 50)
    print("\nBedrock is working correctly.")

except ImportError:
    print("langchain-aws is not installed. Run: pip install langchain-aws")
    sys.exit(1)
except Exception as e:
    print(f"\nBedrock test failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
