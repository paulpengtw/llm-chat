import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

class LLMClient:
    def __init__(self, api_key=None, base_url=None):
        """初始化LLM客户端
        
        API credentials are loaded from environment variables if not provided:
        - API_KEY: OpenAI API key
        - API_BASE_URL: API base URL
        
        Args:
            api_key: Optional override for API key
            base_url: Optional override for base URL
        """
        # Use provided values or fall back to environment variables
        self.api_key = api_key or os.getenv("API_KEY")
        self.base_url = base_url or os.getenv("API_BASE_URL")
        
        if not self.api_key:
            raise ValueError("API key not found. Set API_KEY environment variable or pass api_key parameter.")
        
        if not self.base_url:
            raise ValueError("Base URL not found. Set API_BASE_URL environment variable or pass base_url parameter.")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
    def chat(self, messages, model="deepseek-r1"):
        """与LLM交互
        
        Args:
            messages: 消息列表
            model: 使用的LLM模型
        
        Returns:
            tuple: (content, reasoning_content)
        """
        try:
            print(f"LLM请求: {messages}")
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            if response.choices:
                message = response.choices[0].message
                content = message.content if message.content else ""
                reasoning_content = getattr(message, "reasoning_content", "")
                print(f"LLM推理内容: {content}")
                return content, reasoning_content
            
            return "", ""
                
        except Exception as e:
            print(f"LLM调用出错: {str(e)}")
            return "", ""

# 使用示例
if __name__ == "__main__":
    llm = LLMClient()
    messages = [
        {"role": "user", "content": "你好"}
    ]
    response = llm.chat(messages)
    print(f"响应: {response}")
