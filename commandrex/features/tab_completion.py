import os

def get_completions(text):
    """
    Get possible completions for the given text.
    This function handles both command and file/directory completions.
    """
    if not text:
        return []

    # Split the text into directory and partial name
    directory, partial = os.path.split(text)

    if not directory:
        directory = '.'

    try:
        # Get all files and directories in the specified directory
        names = os.listdir(directory)
    except OSError:
        return []

    # Filter and return matching names
    return [os.path.join(directory, name) for name in names if name.startswith(partial)]

def complete(text):
    """
    Complete the given text and return the completed text.
    """
    completions = get_completions(text)
    
    if not completions:
        return text

    # Find the common prefix
    common_prefix = os.path.commonprefix(completions)
    
    if len(completions) == 1:
        # If there's only one completion, return it
        return completions[0]
    elif common_prefix != text:
        # If there's a common prefix longer than the current text, return it
        return common_prefix
    else:
        # If there are multiple completions, print them
        print("\nPossible completions:")
        for completion in completions:
            print(os.path.basename(completion))
        return text