import os
from openai import AzureOpenAI

from ai.base import BaseAIModel, ModelResult


class AzureOpenAIModel(BaseAIModel):
    PRICING = {
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
        'gpt-4o': {'input': 2.50, 'output': 10.00},
    }

    def __init__(
        self,
        endpoint: str = None,
        api_key: str = None,
        deployment: str = None,
        api_version: str = "2024-12-01-preview"
    ):
        self._endpoint = endpoint or os.getenv('AZURE_ENDPOINT')
        self._api_key = api_key or os.getenv('AZURE_API_KEY')
        self._deployment = deployment or os.getenv('AZURE_DEPLOYMENT')
        self._api_version = api_version
        
        self._client = AzureOpenAI(
            api_version=self._api_version,
            azure_endpoint=self._endpoint,
            api_key=self._api_key,
        )

    @property
    def name(self) -> str:
        return self._deployment

    def _calculate_cost(self, prompt: str, response) -> tuple:
        rates = self.PRICING.get(self._deployment, self.PRICING['gpt-4o-mini'])
        
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.completion_tokens

        input_cost = (input_tokens / 1_000_000) * rates['input']
        output_cost = (output_tokens / 1_000_000) * rates['output']
        total_cost = input_cost + output_cost

        print(f"--- Cost Report ({self._deployment}) ---")
        print(f"Input:  {input_tokens:,} tokens (${input_cost:.4f})")
        print(f"Output: {output_tokens:,} tokens (${output_cost:.4f})")
        print(f"Total:  ${total_cost:.4f}")

        return input_tokens, output_tokens, total_cost

    def generate(self, prompt: str, system_instruction: str = "", temperature: float = 0.1) -> ModelResult:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                messages=messages,
                max_tokens=4096,
                temperature=temperature,
                model=self._deployment
            )
            content = response.choices[0].message.content
            input_tokens, output_tokens, cost = self._calculate_cost(prompt, response)
            return ModelResult(
                model_name=self._deployment,
                content=content,
                success=True,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost
            )
        except Exception as e:
            return ModelResult(model_name=self._deployment, content="", success=False, error=str(e))
