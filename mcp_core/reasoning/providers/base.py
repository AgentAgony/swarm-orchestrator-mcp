
from abc import ABC, abstractmethod
from typing import Optional

class BaseProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generate text from the model.
        
        Args:
            prompt: User prompt
            system_instruction: Optional system context
            
        Returns:
            Generated text content
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the specific model identifier used."""
        pass
