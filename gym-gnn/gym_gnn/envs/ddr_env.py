# Sections that need implementing:
# 1. Actual environment providing obs and rewards for actions
# 2. Different deman matrix generation strategies
# 3. A simple way to couple the above two parts

from typing import Tuple, List, Dict, Callable, Generator, Type
import gym
from gym import error, spaces, utils
from gym.utils import seeding
import networkx
import numpy as np

# Definition of the Routing type (will probablly change)
Routing = Type[np.ndarray]
DemandMatrix = Type[np.ndarray]
DMMemory = List[np.ndarray]
Action = Type[np.ndarray]

class DDREnv(gym.Env):
    """
    Gym env for data driven routing
    Observations are: last k routing and DMs
    Actions are: a routing (standard version: dest splitting ratios, softmin
    version: edge weigths)
    Actions are fully specified routing. Subclass to either take a less
    specified version and transform otherwise learner will need to change too
    Rewards are: utilisation compared to maximum utilisation
    """

    def __init__(self, dm_generator_getter:
            Callable[[],Generator[DemandMatrix, None, None]],
            dm_memory_length: int, graph: networkx.Graph):
        """
        Args:
        dm_generator_getter: a function that returns a genrator for demand
        matrices (so can reset)
        dm_memory_length: the length of the dm history we should train on
        graph: the graph we will be routing over
        """
        self.dm_generator_getter = dm_generator_getter
        self.dm_generator = dm_generator_getter()
        self.dm_memory_length = dm_memory_length
        self.dm_memory: List[DemandMatrix] = []
        self.graph = graph

    def step(self, action) -> Tuple[DMMemory, float, bool, Dict[None, None]]:
        """
        Args:
        action: a routing this is a fully specified routing
        Returns:
        history of dms and the other bits and pieces expected (use np.stack on the history for training)
        """
        # update dm and history
        new_dm = next(self.dm_generator)
        self.dm_memory.append(new_dm)
        if (len(self.dm_memory) > self.dm_memory_length):
            self.dm_memory.pop(0)
        routing = self.get_routing(action)
        reward = self.get_reward(routing)
        # work out when to set done
        return (self.dm_memory.copy(), reward, False, dict())

    def reset(self) -> DMMemory:
        self.dm_generator = self.dm_generator_getter()
        self.dm_memory = [next(self.dm_generator)]
        return self.dm_memory.copy()

    def render(self, mode='human'):
        pass

    def close(self):
        pass

    def get_routing(self, action: Action) -> Routing:
        """
        Subclass to use different actions, assumes action is a routing in base
        case
        """
        return action

    def get_reward(self, routing: Routing) -> float:
        """
        Reward calculated as utilisation of graph given routing compared to
        optimal. May have to call external libraries to calculate efficiently.
        """
        utilisation = self.calc_utilisation(self.graph, self.dm_memory[0],
                                            routing)
        opt_utilisation = self.calc_opt_utilisation(self.graph,
                                                    self.dm_memory[0])
        return -(utilisation/opt_utilisation)

    def calc_opt_utilisation(self, graph: networkx.Graph,
                             demand_matrix: DemandMatrix) -> float:
        """
        Calculates optimal utilisation given demand matrix and graph
        """
        return 0.0

    def calc_utilisation(self, graph: networkx.Graph,
                         demand_matrix: DemandMatrix,
                         routing: Routing) -> float:
        """
        Calculates utilisation of grpah given dm and routing
        """
        return 0.0

class DDREnvDestSplitting(DDREnv):
    """
    DDR Env where all routes are destination based (i.e. each edge has
    ratios for traffic based only on destination)
    """
    def get_routing(self, splitting_ratios) -> Routing:
        pass

class DDREnvSoftmin(DDREnv):
    """
    DDR Env where all softmin routing is used (from Leanring to Route with
    Deep RL paper). Routing is a songle weight per edge, transformed to
    splitting ratios for input to the optimizer calculation.
    """
    def get_routing(self, edge_weights) -> Routing:
        pass

# Need to add
#  1. Sample dm generator
#  2. Function to calc OPT and u (interface with CPLEX?)

def random_dm_generator(shape: Tuple[int, int], seed: int, length: int):
    random_state = np.random.RandomState(seed=seed)
    for _ in range(length):
        yield random_state.random_sample(shape)

def gravity_dm_generator(shape: Tuple[int, int], length: int):
    pass

def calc_opt_utilisation(graph: networkx.Graph,
                         demand_matrix: DemandMatrix) -> float:
    """
    Uses CPLEX LP solver to calculate the optimal max link utilisation
    """
    pass
