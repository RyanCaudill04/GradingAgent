import requests
import base64
import re
from urllib.parse import urlparse
from pathlib import Path

def fetch_github_file_to_txt(github_url, filename, output_file=None, github_token=None):
    """
    Fetch a file from a GitHub repository and save it to a text file.
    
    Args:
        github_url (str): GitHub repository URL (e.g., "https://github.com/owner/repo")
        filename (str): Path to the file within the repository (e.g., "src/main.py")
        output_file (str, optional): Output filename. If None, uses original filename with .txt extension
        github_token (str, optional): GitHub personal access token for private repos
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Parse GitHub URL to extract owner and repo
        parsed_url = urlparse(github_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            print("Error: Invalid GitHub URL format")
            return False
        
        owner = path_parts[0]
        repo = path_parts[1]
        
        # Construct API URL
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
        
        # Set up headers
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Python-GitHub-Fetcher"
        }
        
        # Add authentication if token provided
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        # Make API request
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 404:
            print(f"Error: File '{filename}' not found in repository")
            return False
        elif response.status_code == 403:
            print("Error: Access forbidden. Check if repo is private and token is valid")
            return False
        elif response.status_code != 200:
            print(f"Error: API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Parse JSON response
        file_data = response.json()
        
        # Check if it's actually a file (not a directory)
        if file_data.get('type') != 'file':
            print(f"Error: '{filename}' is not a file")
            return False
        
        # Decode base64 content
        if 'content' not in file_data:
            print("Error: No content found in API response")
            return False
        
        try:
            file_content = base64.b64decode(file_data['content']).decode('utf-8')
        except UnicodeDecodeError:
            # Try with different encoding for binary files
            try:
                file_content = base64.b64decode(file_data['content']).decode('latin-1')
                print("Warning: File decoded with latin-1 encoding (might be binary)")
            except UnicodeDecodeError:
                print("Error: Unable to decode file content (likely binary file)")
                return False
        
        # Determine output filename
        if output_file is None:
            # Use original filename with .txt extension
            original_name = Path(filename).stem
            output_file = f"output/{original_name}.txt"
        else:
            output_file = f"output/{output_file}"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"Successfully saved '{filename}' to '{output_file}'")
        print(f"File size: {len(file_content)} characters")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error: Network request failed - {e}")
        return False
    except Exception as e:
        print(f"Error: Unexpected error - {e}")
        return False
