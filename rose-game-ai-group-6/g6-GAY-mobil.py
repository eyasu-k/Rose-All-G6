"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA

driver_name = "g6 2- GAY MOBIL"


MAX_DEPTH = 5
PATH_SCORE_IDX = 0
PATH_ACTION_IDX = 1

#default rewards when the driver interacts with the objects listed below
REWARDS = {
    obstacles.NONE: 0,
    obstacles.HOTDOG: 5,
    obstacles.TOMATO: -10,
    obstacles.BURGER: 10,
    obstacles.SALAD: -10,
    obstacles.PIZZA: 4,
    obstacles.BROCOLI: -10,
    obstacles.SAUCE: 0,
}

PUNISH = -10
NEUTRAL = 0

#dictionary of special actions required to acquire when reaching special objects
SPECIAL_ACTIONS = {
    obstacles.BURGER: actions.PICKUP,
    obstacles.HOTDOG: actions.JUMP,
    obstacles.PIZZA: actions.BRAKE,
}

# Mirrors rose.engine.config.sauce_multiplier / sauce_effect_hits on the
# engine side - the AI package has no access to that module, so these must
# be kept in sync by hand if the engine values ever change.
SAUCE_MULTIPLIER = 1.15
SAUCE_EFFECT_HITS = 3


class DriveEngine:
    def __init__(self, world):
        self.__world = world
        self.__car_x = world.car.x
        self.__car_y = world.car.y
        
        self.__possible_paths = []

    def get_obj(self, x: int, y: int) -> str:
        try:
            obj = self.__world.get((x, y))
            return obj
        except IndexError:
            print("Exception raised")
            return None
    
    def get_object_reward(self, x: int, y: int) -> str:
        obj = self.get_obj(x, y)
        return REWARDS.get(obj, NEUTRAL)

    def get_best_action(self):
        self.__possible_paths = []
        sauce_charges = getattr(self.__world.car, "sauce_hits_left", 0) or 0
        self.__scan_tree(self.__car_x, 0, 0, actions.NONE, sauce_charges)

        self.__possible_paths.sort(key=lambda path_tuple: path_tuple[PATH_SCORE_IDX], reverse=True)

        best_action = self.__possible_paths[0][PATH_ACTION_IDX]
        return best_action

    def __scan_tree(self, current_x, current_depth, current_score, first_step_action, sauce_charges):
        current_x = current_x % 3
        if current_depth == MAX_DEPTH:
            self.__possible_paths.append((current_score, first_step_action))
            return

        next_y = self.__car_y - 1 - current_depth

        possible_moves = [(current_x, actions.NONE)]
        if current_x > 0:
            possible_moves.append((current_x - 1, actions.LEFT))

        if current_x < 2:
            possible_moves.append((current_x + 1, actions.RIGHT))

        for next_x, next_action in possible_moves:
            obj = self.get_obj(next_x, next_y)
            cell_reward = REWARDS.get(obj, NEUTRAL)
            next_sauce_charges = sauce_charges

            # Simulate the sauce buff along this path: taking a sauce
            # (re)arms the next SAUCE_EFFECT_HITS food hits, and while armed
            # every food hit's reward is amplified and consumes one charge.
            if obj == obstacles.SAUCE:
                next_sauce_charges = SAUCE_EFFECT_HITS
            elif obj not in (obstacles.NONE, None) and sauce_charges > 0:
                cell_reward = round(cell_reward * SAUCE_MULTIPLIER)
                next_sauce_charges = sauce_charges - 1

            step_action = first_step_action
            if current_depth == 0:
                step_action = next_action

            self.__scan_tree(
                current_x=next_x,
                current_depth=current_depth + 1,
                current_score=current_score + cell_reward,
                first_step_action=step_action,
                sauce_charges=next_sauce_charges,
            )

            
def drive(world):
    engine = DriveEngine(world)
    return engine.get_best_action()
