"""Built-in optimization strategies."""

from sim_utils.ml.strategies.base import OptimizerStrategy
from sim_utils.ml.strategies.cmaes import CMAESStrategy
from sim_utils.ml.strategies.composition import PortfolioStrategy, StagedStrategy
from sim_utils.ml.strategies.random import RandomStrategy
from sim_utils.ml.strategies.sobol import SobolStrategy

RandomSearchStrategy = RandomStrategy

__all__ = [
    "OptimizerStrategy",
    "RandomStrategy",
    "RandomSearchStrategy",
    "SobolStrategy",
    "CMAESStrategy",
    "PortfolioStrategy",
    "StagedStrategy",
]
