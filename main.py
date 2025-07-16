import src.Agent as Agent

agent = Agent.Agent(
    repo_name="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
    model_id="mistral-7b-instruct-v0.2.Q4_0"
)
print("\n\n\n\nTesting model...")
agent.analyze_file(file="Team.java", url="https://github.com/RyanCaudill04/Design-Patterns/", folder="strategy")