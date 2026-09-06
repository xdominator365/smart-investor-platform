from abc import ABC, abstractmethod
import pandas as pd

class TradingStrategy(ABC):
    
    @classmethod
    @abstractmethod
    def get_id(cls) -> str:
        """Returns the unique identifier for the strategy."""
        pass
        
    @classmethod
    @abstractmethod
    def get_metadata(cls) -> dict:
        """
        Returns beginner-friendly metadata for the UI.
        Should include 'name', 'description', 'expected_win_rate', and 'risk_level'.
        """
        pass
        
    @classmethod
    @abstractmethod
    def get_risk_parameters(cls) -> dict:
        """
        Returns the specific risk limits for this strategy.
        Should include 'hard_stop_pct', 'trailing_stop_pct', 'max_allocation_pct', and 'max_hold_days'.
        """
        pass
        
    @classmethod
    @abstractmethod
    def generate_signal(cls, df: pd.DataFrame, news_insights: dict | None = None) -> dict:
        """
        Evaluates the dataframe and returns a beginner-friendly signal dict:
        {
            "signal": "BUY" | "SELL" | "HOLD",
            "confidence": float,
            "reason": str (Must be in simple, non-jargon language)
        }
        """
        pass

