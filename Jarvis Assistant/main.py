from speech_recognition import Microphone, Recognizer
from difflib import SequenceMatcher
import json

class Assistant(object):
    """Base class for all Assistants."""

    def __init__(self, intents: str) -> None:
        """Create an Assistant object."""
        with open(intents) as file:
            self.intents = file.read()
    
    def _check_compatability(self, sequence: str, to_compare: str):
        return SequenceMatcher(sequence, to_compare).ratio()
    
    def parse_intents(self):
        json.loads(self.intents)

    def run(self) -> None:
        pass

if __name__ == "__main__":
    assistant = Assistant()
    assistant.run()
