"""
LLM Integration Module
Handles response generation using various LLM providers
"""

import os
from typing import List, Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response from prompt"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider (GPT models)"""

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI provider

        Args:
            model_name: Model to use (gpt-4, gpt-3.5-turbo, etc.)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        logger.info(f"Initialized OpenAI provider with model: {model_name}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider (Claude models)"""

    def __init__(self, model_name: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic provider

        Args:
            model_name: Claude model to use
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name
        logger.info(f"Initialized Anthropic provider with model: {model_name}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using Anthropic Claude"""
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"


class GoogleAIProvider(LLMProvider):
    """Google AI LLM provider (Gemini models)"""

    def __init__(self, model_name: str = "gemini-pro"):
        """
        Initialize Google AI provider

        Args:
            model_name: Gemini model to use (gemini-pro, gemini-pro-vision, etc.)
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        logger.info(f"Initialized Google AI provider with model: {model_name}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using Google AI Gemini"""
        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Check if response was blocked
            if hasattr(response, 'prompt_feedback'):
                block_reason = response.prompt_feedback.block_reason
                if block_reason:
                    logger.warning(f"Response blocked: {block_reason}")
                    return f"Response was blocked due to: {block_reason}"

            # Handle multi-part responses
            # Always try to extract from candidates first for most reliable results
            text_parts = []
            try:
                if response.candidates:
                    logger.info(f"Number of candidates: {len(response.candidates)}")
                    for idx, candidate in enumerate(response.candidates):
                        logger.info(f"Candidate {idx} - Finish reason: {candidate.finish_reason}")
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            logger.info(f"Candidate {idx} has {len(candidate.content.parts)} parts")
                            for part_idx, part in enumerate(candidate.content.parts):
                                if hasattr(part, 'text'):
                                    part_text = part.text
                                    logger.info(f"Part {part_idx} text length: {len(part_text)}")
                                    text_parts.append(part_text)
                                else:
                                    logger.warning(f"Part {part_idx} has no text attribute")

                result = ''.join(text_parts)
                logger.info(f"Combined result length: {len(result)}")

                if not result or result.strip() == "":
                    logger.warning("Received empty response from Gemini")
                    if response.candidates:
                        finish_reason = response.candidates[0].finish_reason
                        safety_ratings = response.candidates[0].safety_ratings
                        logger.info(f"Finish reason: {finish_reason}")
                        logger.info(f"Safety ratings: {safety_ratings}")
                        return f"Empty response received. Finish reason: {finish_reason}"
                    return "Empty response received from the model."

                return result

            except AttributeError as ae:
                logger.error(f"AttributeError accessing response parts: {ae}")
                # Fallback to simple text accessor
                try:
                    text = response.text
                    logger.info(f"Fallback to response.text, length: {len(text)}")
                    return text
                except Exception as e2:
                    logger.error(f"Could not access response.text either: {e2}")
                    logger.error(f"Response object: {response}")
                    return f"Error: Could not access response text - {str(ae)}"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"


class LocalLLMProvider(LLMProvider):
    """Local LLM provider using transformers"""

    def __init__(self, model_name: str = "facebook/opt-350m"):
        """
        Initialize local LLM provider

        Args:
            model_name: Hugging Face model name
        """
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
        except ImportError:
            raise ImportError("Transformers not installed. Install with: pip install transformers torch")

        self.model_name = model_name
        logger.info(f"Loading local model: {model_name} (this may take a while...)")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

        # Set pad token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        logger.info(f"Local model loaded: {model_name}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate response using local model"""
        try:
            import torch

            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)

            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.pad_token_id
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove the input prompt from response
            response = response[len(prompt):].strip()

            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"


class ResponseGenerator:
    """
    High-level interface for generating responses using LLMs
    """

    def __init__(
        self,
        provider: str = "anthropic",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize response generator

        Args:
            provider: LLM provider ('openai', 'anthropic', 'google', 'local')
            model_name: Specific model name (optional)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
        """
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize provider
        if provider == "openai":
            default_model = "gpt-3.5-turbo"
            self.llm = OpenAIProvider(model_name or default_model)
        elif provider == "anthropic":
            default_model = "claude-3-sonnet-20240229"
            self.llm = AnthropicProvider(model_name or default_model)
        elif provider == "google":
            default_model = "gemini-pro"
            self.llm = GoogleAIProvider(model_name or default_model)
        elif provider == "local":
            default_model = "facebook/opt-350m"
            self.llm = LocalLLMProvider(model_name or default_model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        logger.info(f"Initialized ResponseGenerator with {provider} provider")

    def generate_response(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response for a query with context

        Args:
            query: User query
            context: Retrieved context
            system_prompt: Optional system prompt

        Returns:
            Generated response
        """
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant. Answer the user's question based on the provided context.
Be concise, accurate, and cite the source when possible. If the answer cannot be found in the context, say so clearly."""

        # Build complete prompt
        prompt = f"""{system_prompt}

CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:"""

        # Generate response
        logger.info("Generating response...")
        response = self.llm.generate(
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response

    def generate_conversational_response(
        self,
        query: str,
        context: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate response with conversation history

        Args:
            query: Current user query
            context: Retrieved context
            conversation_history: List of previous messages

        Returns:
            Generated response
        """
        # Build prompt with history
        prompt_parts = [
            "You are a helpful AI assistant. Use the following context to answer questions.\n"
        ]

        if conversation_history:
            prompt_parts.append("\nCONVERSATION HISTORY:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt_parts.append(f"{role.upper()}: {content}")

        prompt_parts.append(f"\nCONTEXT:\n{context}")
        prompt_parts.append(f"\nUSER QUESTION:\n{query}")
        prompt_parts.append("\nANSWER:")

        prompt = "\n".join(prompt_parts)

        response = self.llm.generate(
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response


class ConversationMemory:
    """
    Manages conversation history for multi-turn interactions
    """

    def __init__(self, max_history: int = 10):
        """
        Initialize conversation memory

        Args:
            max_history: Maximum number of messages to store
        """
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """
        Add a message to history

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        self.history.append({
            'role': role,
            'content': content
        })

        # Keep only last max_history messages
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.history.copy()

    def clear_history(self):
        """Clear conversation history"""
        self.history = []

    def get_history_text(self) -> str:
        """Get history as formatted text"""
        lines = []
        for msg in self.history:
            role = msg['role'].upper()
            content = msg['content']
            lines.append(f"{role}: {content}")
        return "\n".join(lines)


if __name__ == "__main__":
    # Test response generation
    print("LLM integration module loaded successfully")

    # Example usage (requires API keys)
    # generator = ResponseGenerator(provider="anthropic")
    # response = generator.generate_response(
    #     query="What is machine learning?",
    #     context="Machine learning is a subset of AI that enables systems to learn from data."
    # )
    # print(response)
