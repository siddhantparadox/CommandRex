import os
from dotenv import load_dotenv
import logging
from anthropic import Anthropic
from .nlp_advanced import AdvancedNLP

# Set up logging to file
logging.basicConfig(filename='commandrex_debug.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('ANTHROPIC_API_KEY')
logger.debug(f"API Key loaded: {'Yes' if API_KEY else 'No'}")

# Initialize Anthropic client
anthropic = Anthropic(api_key=API_KEY)

# Initialize AdvancedNLP (spaCy-based) as a fallback
advanced_nlp = AdvancedNLP()

def process_command(user_input):
    """
    Process the user's natural language input using Claude API first, 
    falling back to spaCy-based AdvancedNLP if Claude is unavailable.
    """
    try:
        logger.info(f"Processing command: {user_input}")

        # Try Claude API first
        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Translate the following natural language command to a Windows command: {user_input}. 
                    Respond with ONLY the Windows command, nothing else. If it's not a valid command, respond with 'INVALID'.
                    For 'show me users', the correct Windows command is 'net user'.
                    """
                }
            ]
        )
        logger.info(f"Received response from Claude API: {response.content}")
        
        # Extract the command from the response
        command = response.content[0].text.strip()
        
        # Remove any markdown code block syntax
        command = command.replace('```', '').strip()
        
        logger.info(f"Processed command: {command}")
        
        return command if command.lower() != 'invalid' else None

    except Exception as e:
        logger.error(f"An error occurred while communicating with the Claude API: {e}")
        if hasattr(e, 'response'):
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        
        # Fallback to spaCy-based AdvancedNLP
        logger.info("Falling back to spaCy-based AdvancedNLP")
        return fallback_process_command(user_input)

def fallback_process_command(user_input):
    """
    Fallback method using spaCy-based AdvancedNLP when Claude API is unavailable.
    """
    try:
        advanced_interpretation = advanced_nlp.process_command(user_input)
        logger.info(f"AdvancedNLP interpretation: {advanced_interpretation}")

        if not advanced_interpretation.get('unmatched', False):
            windows_command = construct_windows_command(advanced_interpretation)
            if windows_command:
                return windows_command

        return None  # If AdvancedNLP couldn't interpret the command
    except Exception as e:
        logger.error(f"An error occurred in fallback processing: {e}")
        return None

def construct_windows_command(interpretation):
    """
    Construct a Windows command based on the AdvancedNLP interpretation.
    """
    if interpretation['operation'] == 'create':
        if interpretation['target_type'] == 'directory':
            return f"mkdir \"{interpretation['name']}\""
        elif interpretation['target_type'] == 'file':
            return f"type nul > \"{interpretation['name']}\""
    elif interpretation['operation'] in ['delete', 'remove']:
        if interpretation['target_type'] == 'directory':
            return f"rmdir \"{interpretation['name']}\""
        elif interpretation['target_type'] == 'file':
            return f"del \"{interpretation['name']}\""
    
    return None

if __name__ == "__main__":
    # Test the function
    test_inputs = [
        "Create a new folder called Project Files",
        "Delete the file named old_report.txt",
        "Show me all running processes",
        "Remove the folder temp_data"
    ]
    for test_input in test_inputs:
        result = process_command(test_input)
        print(f"Input: {test_input}")
        print(f"Output: {result}\n")