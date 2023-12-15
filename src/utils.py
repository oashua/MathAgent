import re

class JsonError(BaseException):
    # extract Json/Json list
    def __init__(self, message):
        self.message = message
        
def return_json(text):
    text = text.replace('\n\n', ' ').replace('\n', ' ')
    try:
        return eval(text)
    except:
        pass
    
    try:
        json_pattern = r'\{.*\}'
        json_match = re.search(json_pattern, text)
        return eval(json_match.group())
    except Exception as e:
        error = f'''
The original text is:
{text}

The error is
{str(e)}'''
        raise JsonError(error)