from .base_strategy import TradingStrategy
from .trend_following import TrendFollowingStrategy
from .mean_reversion import MeanReversionStrategy

class StrategyRegistry:
    _strategies = {
        TrendFollowingStrategy.get_id(): TrendFollowingStrategy,
        MeanReversionStrategy.get_id(): MeanReversionStrategy
    }

    @classmethod
    def get_strategy(cls, strategy_id: str) -> type[TradingStrategy]:
        strategy = cls._strategies.get(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy '{strategy_id}' not found.")
        return strategy

    @classmethod
    def get_all_metadata(cls) -> list[dict]:
        return [
            {"id": s_id, **strategy.get_metadata()}
            for s_id, strategy in cls._strategies.items()
        ]

