"""Built-in optimization strategies."""

from phys_sims_utils.ml.strategies.base import OptimizerStrategy
from phys_sims_utils.ml.strategies.cmaes import CMAESStrategy
from phys_sims_utils.ml.strategies.composition import PortfolioStrategy, StagedStrategy
from phys_sims_utils.ml.strategies.random import RandomStrategy
from phys_sims_utils.ml.strategies.sobol import SobolStrategy

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
