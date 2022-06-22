from mesa import Model, Agent
from mesa.datacollection import DataCollector
from mesa.time import SimultaneousActivation


class SmallWorldAgentBasic(Agent):

    def __init__(self, unique_id, neighbors,  model):
        '''
         Create a new small world agent.

         Args:
            unique_id: Unique identifier for the agent
            neighbors: list of directly reachable agents
        '''

        super().__init__(unique_id, model)
        self.neighbors = neighbors

        self.infected = False
        self.newly_infected = False
        self.dead = False
        self.candidate_infections = []

    def step(self):
        '''
        Run one step of the agent.
        '''
        self.candidate_infections = []
        if self.dead:
            return

        if self.newly_infected:
            self.infected = True

        if self.infected:
            for neighbor in self.neighbors:
                if self.model.random.random() < self.model.infect_probability:
                    self.candidate_infections.append(neighbor)

    def advance(self):
        '''
        advance step of model
        '''

        if self.dead:
            return

        if self.infected:
            for candidate in self.candidate_infections:
                candidate.newly_infected = True
                print("Agent "+str(candidate.unique_id)+" got infected.\n")
            self.dead = True
            print("Agent "+str(self.unique_id)+" died.\n")


class SmallWorldModel(Model):

    def __init__(self, N, k, p, r):
        '''
        Create a new small world model.

         Args:
            N: how many agents the model contains
            k: how many neighbors an agent has CURRENTLY ONLY EVEN K SUPPORTED
            p: probability of rearranging edge in initialization
            r: probability of infecting another agent
        '''

        super().__init__()

        # 1 Initialization
        self.num_agents = N
        self.num_neighbors = k
        self.swap_probability = p
        self.infect_probability = r

        self.schedule = SimultaneousActivation(self)
        '''
        self.datacollector = DataCollector(  # < Note that we have both an agent and model data collector
            model_reporters={"Opinion_groups": get_number_opinion_groups}, agent_reporters={"Opinion": "opinion"}
        )
        '''
        # Create agents
        for i in range(self.num_agents):
            agent = SmallWorldAgentBasic(i, [0]*k, self)
            self.schedule.add(agent)

        agents = self.schedule.agents

        # make the k nearest neighbors the official neighbors
        for j in range(int(self.num_neighbors / 2)):
            for i in range(self.num_agents):
                right = (i + j + 1) % self.num_agents
                left = (i - j - 1) % self.num_agents
                agents[i].neighbors[j*2] = agents[right]
                agents[i].neighbors[j*2+1] = agents[left]

        # randomly replace neighbors with new neighbors
        for j in range(self.num_neighbors):
            for i in range(self.num_agents):
                if self.random.random() < self.swap_probability:
                    candidate_agent = self.random.choice(self.schedule.agents)
                    already_connected = True
                    while already_connected:
                        in_neighbors = False
                        for neighbor in agents[i].neighbors:
                            if neighbor == candidate_agent:
                                in_neighbors = True
                        if in_neighbors:
                            candidate_agent = self.random.choice(self.schedule.agents)
                            already_connected = True
                        else:
                            already_connected = False
                    agents[i].neighbors[j] = candidate_agent
                    print("Agent "+str(i)+"'s new Neighbor on position "+str(j)+" is now Agent "+str(candidate_agent.unique_id)+".\n")

        # infect 1 agent
        patient_zero = self.random.choice(self.schedule.agents)
        patient_zero.infected = True
        print("Agent " + str(patient_zero.unique_id) + " got infected.\n")



    def step(self):
        '''
        Run one step of the model. If All agents are happy, halt the model.
        '''

        # 3 Step model function
        # self.datacollector.collect(self)
        self.schedule.step()


model = SmallWorldModel(100, 4, 0.2, 0.5)
while model.schedule.steps < 100:
    model.step()
