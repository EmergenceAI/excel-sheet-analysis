"""LLM Client for interacting with AI providers (Anthropic Claude, OpenAI)."""

import os
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic
import openai

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLM APIs."""

    def __init__(self, config: Dict):
        """
        Initialize LLM client.

        Args:
            config: Configuration dictionary with LLM settings
        """
        self.provider = config.get('provider', 'anthropic')
        self.model = config.get('model', 'claude-sonnet-4')
        self.max_tokens = config.get('max_tokens', 8000)
        self.temperature = config.get('temperature', 0.1)

        # Get API key from environment
        api_key_env = config.get('api_key_env', 'ANTHROPIC_API_KEY')
        self.api_key = os.getenv(api_key_env)

        if not self.api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env}")

        # Initialize client based on provider
        if self.provider == 'anthropic':
            self.client = Anthropic(api_key=self.api_key)
        elif self.provider == 'openai':
            openai.api_key = self.api_key
            self.client = openai
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

        logger.info(f"Initialized LLM client: {self.provider} / {self.model}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate completion from LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context

        Returns:
            Generated text from LLM
        """
        try:
            if self.provider == 'anthropic':
                return self._generate_anthropic(prompt, system_prompt)
            elif self.provider == 'openai':
                return self._generate_openai(prompt, system_prompt)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    def _generate_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Anthropic Claude."""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _generate_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using OpenAI."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        return response.choices[0].message.content

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict:
        """
        Generate JSON response from LLM.

        Args:
            prompt: The user prompt (should specify JSON output)
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON dictionary
        """
        import json

        response = self.generate(prompt, system_prompt)

        # Extract JSON from response (may be wrapped in markdown code blocks)
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response was: {response}")
            raise
