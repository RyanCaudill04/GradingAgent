import Agents.CloudAgent as CloudAgent
import os

class Benchmark:
  def __init__(self):
    self.agents = []
    self.load_agents()

  def load_agents(self):
    models = os.listdir("models")
    for model in models:
      agent = CloudAgent.Agent(model_id=model)
      self.agents.append(agent)