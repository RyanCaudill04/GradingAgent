from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import src.Github as Github
from pathlib import Path
import torch
import os

class LLamaAgent:
    def __init__(self, repo_name: str, model_id: str):
      self.repo_name = repo_name          # e.g. "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
      self.model_id = model_id            # e.g. "mistral-7b-instruct-v0.2.Q4_0"
      self.cache_dir = os.path.expanduser(f"models/{self.model_id}")
      self.gguf_file_path = os.path.join(self.cache_dir, f"{self.model_id}.gguf")
        
      if not os.path.isfile(self.gguf_file_path):
        print(f"Model not found locally, downloading to {self.gguf_file_path}...")
        self.gguf_file_path = hf_hub_download(
          repo_id=self.repo_name,
          filename=f"{self.model_id}.gguf",
          cache_dir=self.cache_dir,
        )
      else:
        print(f"Using cached model at {self.gguf_file_path}")
        
        self.llm = Llama(model_path=self.gguf_file_path, n_ctx=2048, n_threads=4)

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
    """
    def generate_text(self, prompt: str, max_tokens=64) -> str:
      response = self.llm(prompt, max_tokens=max_tokens)
      return response["choices"][0]["text"].strip()

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
    def analyze_file(self, file, url, folder=""):
      file_to_analyze = self.get_github_file(file, url, folder)
      with open(file_to_analyze, "r") as f:
        content = f.read()
      self.get_prompt()

      info = f"{self.prompt}\n{self.guidelines}\n\nFile content:\n{content}"
      response = self.generate_text(info, max_tokens=2048)
      self.output_to_file(response)


    def test(self):
      prompt = "What is the capital of France?"
      response = self.llm(prompt, max_tokens=50, stop=["\n"])
      self.output_to_file([{"generated_text": response["choices"][0]["text"].strip()}])