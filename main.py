import src.Agent as Agent

agent = Agent.Agent(
    model_id="deepseek-ai/DeepSeek-R1-0528"
)

agent.analyze_file(file="Team.java", url="https://github.com/RyanCaudill04/Design-Patterns/", folder="strategy")