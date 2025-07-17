import src.Github as Github
from pathlib import Path
from openai import OpenAI
from together import Together
import os

class Agent:
    def __init__(self, model_id: str):
      self.model_id = model_id 
      self.client = OpenAI(
        base_url="https://api.together.xyz/v1",
        api_key=os.getenv("TOGETHER_API_KEY")
      )

    """
    Fetch a file from a GitHub repository, save it to a text file
    Args:
        file (str): The file within the repository (e.g., "main.py")
        url (str): The GitHub repository URL (e.g., "
        folder (str): The folder path within the repository (e.g., "src")
    Returns:
        str: The path to the saved text file
    """
    def get_github_file(self, file, url, folder):
      output = f"{folder}/{file.split('/')[-1].split('.')[0]}.txt"
      Github.fetch_github_file_to_txt(filename=f"{folder}/{file}", github_url=url, output_file=output)
      return f"repos/{output}"

    """
    Load the prompt and guidelines from text files
    This is used to provide context for the model when analyzing files.
    """
    def get_prompt(self):
      with open("prompt/prompt.txt", "r") as f:
        self.prompt = f.read()
      with open("prompt/guidelines.txt", "r") as f:
        self.guidelines = f.read()

    """
    Takes prompt and generates text using the model
    Args:
        prompt (str): The input prompt for the model
        model_id (str): The model identifier (e.g., "deepseek-ai/DeepSeek-R1-0528")
        max_tokens (int): The maximum number of tokens to generate
    Returns:
        str: The generated text from the model
    """
    def generate_text(self, prompt: str, max_tokens: int = 512) -> str:
      response = self.client.chat.completions.create(
        model=self.model_id,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7,
      )
      return response.choices[0].message.content.strip()


    """
    Takes the response from the model and writes it to an output file
    Args:
        response (list): The response from the model, typically a list of dictionaries
    """
    def output_to_file(self, response):
      with open(f"output/output.txt", "a") as f:
        f.write(f"Response from {self.model_id}:\n{response}\n\n")

    """
    Analyze a file from a GitHub repository using the model
    Args:
        file (str): The file to analyze (e.g., "main.py")
        url (str): The GitHub repository URL (e.g., "
        folder (str): The folder path within the repository (e.g., "src")
    """
    def analyze_file(self, file: str, url: str, max_tokens: int = 512, folder=""):
      file_to_analyze = self.get_github_file(file, url, folder)
      with open(file_to_analyze, "r") as f:
        content = f.read()
      self.get_prompt()

      info = f"{self.prompt}\n{self.guidelines}\n\nFile content:\n{content}"
      response = self.generate_text(info)
      self.output_to_file(response)


    def test(self):
      prompt = "What is the capital of France?"
      response = self.llm(prompt, max_tokens=50, stop=["\n"])
      self.output_to_file([{"generated_text": response["choices"][0]["text"].strip()}])