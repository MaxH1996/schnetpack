from __future__ import annotations
import torch

from abc import ABC
from typing import TYPE_CHECKING, List, Dict, Optional
from schnetpack.md.calculators import MDCalculator

if TYPE_CHECKING:
    from schnetpack.md import System

__all__ = ["EnsembleCalculator"]


class EnsembleCalculator(ABC, MDCalculator):
    """
    Mixin for creating ensemble calculators from the standard `schnetpack.md.calculators` classes. Accumulates
    property predictions as the average over all models and uncertainties as the variance of model predictions.
    """

    def calculate(self, system: System):
        """
        Perform all calculations and compyte properties and uncertainties.

        Args:
            system (schnetpack.md.System): System from the molecular dynamics simulation.
        """
        inputs = self._generate_input(system)

        results = []
        for model in self.models:
            prediction = model(inputs)
            results.append(prediction)

        # Compute statistics
        self.results = self._accumulate_results(results)
        self._update_system(system)

    @staticmethod
    def _accumulate_results(
        results: List[Dict[str, torch.tensor]]
    ) -> Dict[str, torch.tensor]:
        # Get the keys
        accumulated = {p: [] for p in results[0]}
        ensemble_results = {p: [] for p in results[0]}

        for p in accumulated:
            tmp = torch.stack([result[p] for result in results])
            ensemble_results[p] = torch.mean(tmp, dim=0)
            ensemble_results["{:s}_var".format(p)] = torch.var(tmp, dim=0)

        return ensemble_results

    def _activate_stress(self, stress_label: Optional[str] = None):
        """
        Routine for activating stress computations
        Args:
            stress_label (str, optional): stess label.
        """
        raise NotImplementedError

    @staticmethod
    def _update_required_properties(required_properties: List[str]) -> List[str]:
        """
        Update required properties to also contain predictive variances.

        Args:
            required_properties (list(str)): List of basic required properties.
        """
        new_required = []
        for p in required_properties:
            if p is not None:
                prop_string = "{:s}_var".format(p)
                new_required += [p, prop_string]
        return new_required
