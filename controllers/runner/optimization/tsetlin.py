from optimization.fitness import Fitness

EXPLORATION_STATE = 3
OPERATIVE_STATE = 3
ADAPTIVE_STATE = 1
ALPHA_MULTIPLIER = 0.95
HISTORY_WEIGHT = 0.7
SIMILARITY_TOLERANCE = 0.5


class Tsetlin:
    best_performance: float = 0
    state: int = EXPLORATION_STATE + int(OPERATIVE_STATE / 2)

    def reward(self):
        # I finished the exploration: move to operative state
        if self.state == 0:
            self.state = EXPLORATION_STATE
        # I am currently exploring solutions: continue
        elif self.state < EXPLORATION_STATE:
            self.state -= 1
        # my performance was stagnating: move towards operating
        elif self.state - EXPLORATION_STATE < int(OPERATIVE_STATE / 2):
            self.state += 1
        # my performance is good: keep operating
        elif self.state - EXPLORATION_STATE == int(OPERATIVE_STATE / 2):
            pass
        # my performance is improving (possibly after an adaptation): move to operating
        elif self.state < OPERATIVE_STATE:
            self.state -= 1
        # my performance is improving after an adaptation: keep adapting
        else:
            pass

    def penalty(self, stagnation=False):
        # I finished the exploration: move to operative state
        if self.state == 0:
            self.state = EXPLORATION_STATE + int(OPERATIVE_STATE / 2)
        # I am currently exploring solutions: continue
        elif self.state < EXPLORATION_STATE:
            self.state -= 1
        # my performance is stagnating: move towards exploration
        elif self.state - EXPLORATION_STATE < int(OPERATIVE_STATE / 2):
            self.state -= 1
        # my performance is stagnating: move towards exploration
        elif self.state - EXPLORATION_STATE == int(OPERATIVE_STATE / 2) and stagnation:
            self.state -= 1
        # my performance is bad: move towards adaptation
        elif self.state - EXPLORATION_STATE == int(OPERATIVE_STATE / 2):
            self.state += 1
        # my performance is decreasing: move to adaptation
        elif self.state < OPERATIVE_STATE:
            self.state += 1
        # my performance is decreasing after an adaptation: move towards operation
        else:
            self.state -= 1

    def update_state(self, fitness: Fitness) -> bool:

        # best performance update
        if EXPLORATION_STATE < self.state <= EXPLORATION_STATE + OPERATIVE_STATE:
            self.best_performance *= HISTORY_WEIGHT
            self.best_performance += (1 - HISTORY_WEIGHT) * fitness.value()
        elif fitness.value() > self.best_performance:
            self.best_performance = fitness.value()

        print(fitness.value(), self.best_performance)
        print(self.state, end=" -> ")
        # state change in Tsetlin machine
        if fitness.value() < ALPHA_MULTIPLIER * self.best_performance:
            self.penalty()
        elif abs(fitness.value() - self.best_performance) < SIMILARITY_TOLERANCE:
            self.penalty(stagnation=True)
        else:
            self.reward()
        print(self.state)

        # return true if the state is adaptive
        return self.state < EXPLORATION_STATE or self.state >= EXPLORATION_STATE + OPERATIVE_STATE


tsetlin = Tsetlin()
