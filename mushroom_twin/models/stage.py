"""Growth stage model: determines the cultivation stage from biological state."""

from ..config import Config
from ..state import TwinState


class StageModel:
    """Determine the current cultivation stage based on the crop's state."""

    def __init__(self):
        self.stages = [
            "Preparation",
            "Inoculation",
            "Spawn Run",
            "Pinhead Formation",
            "Fruiting",
            "Harvesting",
        ]

    def is_preparation(self, state: TwinState) -> bool:
        return state.current_day == 0

    def is_inoculation(self, state: TwinState) -> bool:
        return state.current_day >= 1 and state.colonization < 5

    def is_spawn_run(self, state: TwinState) -> bool:
        return 5 <= state.colonization < Config.PINNING_THRESHOLD

    def is_pinhead(self, state: TwinState) -> bool:
        return (
            state.colonization >= Config.PINNING_THRESHOLD
            and state.pinhead_count > 0
            and state.fruit_weight < 50
        )

    def is_fruiting(self, state: TwinState) -> bool:
        return 50 <= state.fruit_weight < 0.90 * Config.W_MAX

    def is_harvest(self, state: TwinState) -> bool:
        return state.fruit_weight >= 0.90 * Config.W_MAX

    def determine_stage(self, state: TwinState) -> str:
        """Determine the current cultivation stage."""
        if self.is_preparation(state):
            stage = "Preparation"
        elif self.is_inoculation(state):
            stage = "Inoculation"
        elif self.is_spawn_run(state):
            stage = "Spawn Run"
        elif self.is_pinhead(state):
            stage = "Pinhead Formation"
        elif self.is_fruiting(state):
            stage = "Fruiting"
        elif self.is_harvest(state):
            stage = "Harvesting"
        else:
            stage = state.current_stage

        state.current_stage = stage
        return stage

    def update(self, state: TwinState) -> None:
        """Update cultivation stage."""
        self.determine_stage(state)

    def get_stage_status(self, state: TwinState) -> dict:
        """Return stage information."""
        return {
            "Batch ID": state.batch_id,
            "Current Stage": state.current_stage,
            "Current Day": state.current_day,
            "Colonization": state.colonization,
            "Fruit Weight": state.fruit_weight,
            "Pinhead Count": state.pinhead_count,
            "Fruit Count": state.fruit_count,
        }

    def print_status(self, state: TwinState) -> None:
        print("\n" + "=" * 60)
        print("STAGE MODEL")
        print("=" * 60)
        print(f"Batch ID        : {state.batch_id}")
        print(f"Current Day     : {state.current_day}")
        print(f"Current Stage   : {state.current_stage}")
        print(f"Colonization    : {state.colonization:.2f}%")
        print(f"Fruit Weight    : {state.fruit_weight:.2f} g")
        print(f"Pinhead Count   : {state.pinhead_count}")
        print(f"Fruit Count     : {state.fruit_count}")
        print("=" * 60)

    def reset(self, state: TwinState) -> None:
        """Reset stage information."""
        state.current_stage = "Preparation"

    def validate(self, state: TwinState) -> bool:
        """Validate stage information."""
        if state.current_stage not in self.stages:
            return False
        if state.current_day < 0:
            return False
        return True
