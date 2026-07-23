"""Biological respiration model: substrate (Jung & Son 2021) + fruit (Thornley)."""

import math

from ..config import Config
from ..state import TwinState


class RespirationModel:
    """Substrate and fruit respiration, total respiration and respiration heat."""

    def __init__(self):
        # Jung & Son (2021) substrate respiration coefficients
        self.a1 = Config.A1
        self.a2 = Config.A2
        self.a3 = Config.A3

        # Thornley model coefficients
        self.maintenance = Config.MAINTENANCE_COEFFICIENT
        self.growth = Config.GROWTH_COEFFICIENT

        # Heat conversion
        self.heat_coefficient = Config.RESPIRATION_HEAT_COEFFICIENT

        # Previous fruit weight (for growth-rate term)
        self.previous_fruit_weight = 0.0

    def substrate_respiration(self, state: TwinState) -> float:
        """Jung & Son (2021): Rm = a1 * exp(a2 * T) + a3."""
        respiration = self.a1 * math.exp(self.a2 * state.temperature) + self.a3
        respiration = max(0.0, respiration)
        state.substrate_respiration = respiration
        return respiration

    def fruit_respiration(self, state: TwinState) -> float:
        """Thornley respiration: R = M*W + P*(dW/dt)."""
        growth_rate = state.fruit_weight - self.previous_fruit_weight
        respiration = self.maintenance * state.fruit_weight + self.growth * growth_rate
        respiration = max(0.0, respiration)

        self.previous_fruit_weight = state.fruit_weight
        state.fruit_respiration = respiration
        return respiration

    def total_respiration(self, state: TwinState) -> float:
        """Total respiration: Rtotal = Rsubstrate + Rfruit."""
        total = state.substrate_respiration + state.fruit_respiration
        state.total_respiration = total
        return total

    def respiration_heat(self, state: TwinState) -> float:
        """Respiration heat: Q = kr * Rtotal."""
        heat = self.heat_coefficient * state.total_respiration
        state.respiration_heat = heat
        return heat

    def update(self, state: TwinState) -> None:
        """Execute one respiration update step."""
        self.substrate_respiration(state)
        self.fruit_respiration(state)
        self.total_respiration(state)
        self.respiration_heat(state)

    def get_respiration_status(self, state: TwinState) -> dict:
        return {
            "Substrate Respiration": state.substrate_respiration,
            "Fruit Respiration": state.fruit_respiration,
        }

    def get_complete_status(self, state: TwinState) -> dict:
        """Return all respiration-related variables."""
        return {
            "Substrate Respiration": state.substrate_respiration,
            "Fruit Respiration": state.fruit_respiration,
            "Total Respiration": state.total_respiration,
            "Respiration Heat": state.respiration_heat,
        }

    def print_status(self, state: TwinState) -> None:
        print("\n" + "=" * 60)
        print("RESPIRATION MODEL")
        print("=" * 60)
        print(f"Substrate Respiration : {state.substrate_respiration:.3f}")
        print(f"Fruit Respiration     : {state.fruit_respiration:.3f}")
        print("=" * 60)

    def print_complete_status(self, state: TwinState) -> None:
        print("\n" + "=" * 60)
        print("RESPIRATION MODEL")
        print("=" * 60)
        print(f"Substrate Respiration : {state.substrate_respiration:.4f}")
        print(f"Fruit Respiration     : {state.fruit_respiration:.4f}")
        print(f"Total Respiration     : {state.total_respiration:.4f}")
        print(f"Respiration Heat      : {state.respiration_heat:.4f}")
        print("=" * 60)

    def validate(self, state: TwinState) -> bool:
        """Validate respiration variables."""
        if state.substrate_respiration < 0.0:
            return False
        if state.fruit_respiration < 0.0:
            return False
        if state.total_respiration < 0.0:
            return False
        if state.respiration_heat < 0.0:
            return False
        return True
