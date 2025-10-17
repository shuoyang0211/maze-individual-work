from pynput import keyboard
from typing import Optional

from maze_core import Action, GameState, OccupancyGrid

class TeleopAgent:
    """
    Global-key teleop: waits for the next relevant key press and returns an Action.
    """

    def __init__(self) -> None:
        self._name = "Teleop Agent"

        self.pressed = {"up": False, "down": False, "left": False, "right": False, "space": False}

        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release, daemon=True)
        self._listener.start()

    @property
    def name(self) -> str:
        return self._name

    def _on_press(self, key) -> None:
        move = self._map_key(key)
        if move:
            self.pressed[move] = True

        if key == keyboard.Key.esc:
            raise SystemExit

    def _on_release(self, key) -> None:
        move = self._map_key(key)
        if move:
            self.pressed[move] = False

    def _map_key(self, key) -> Optional[str]:
        if key == keyboard.Key.space:
            return "space"

        if isinstance(key, keyboard.KeyCode) and key.char:
            ch = key.char.lower()
            if ch == "w":
                return "up"
            if ch == "s":
                return "down"
            if ch == "a":
                return "left"
            if ch == "d":
                return "right"


        return None

    def get_action(self, game_state: GameState, occupancy_grid: OccupancyGrid, dt: float) -> Action:
        if self.pressed["space"]:
            self.pressed["space"] = False
            if game_state.agent.flag is None:
                return Action.PickupFlag(id=game_state.agent.id)
            else:
                return Action.DropFlag(id=game_state.agent.id)

        horizontal = int(self.pressed["right"]) - int(self.pressed["left"])
        vertical = int(self.pressed["up"]) - int(self.pressed["down"])
        vx, vz = horizontal, -vertical
        norm = (vx**2 + vz**2) ** 0.5
        vx /= max(1, norm)
        vz /= max(1, norm)
        vx *= game_state.agent.max_speed
        vz *= game_state.agent.max_speed

        return Action.Move(id=game_state.agent.id, velocity=(vx, vz))