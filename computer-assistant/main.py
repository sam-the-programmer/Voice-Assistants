import json
import random
from difflib import SequenceMatcher

import text_to_speech as tts
from speech_recognition import Microphone, Recognizer, UnknownValueError


class ComputerAssistant(object):
    """Base class for all Assistants."""

    def __init__(self, intents: str, similarity_threshold: float = 0.5) -> None:
        """Create an Assistant object."""
        with open(intents) as file:
            self._intents = file.read()
        self._max_tag = "nothing"
        self._blank_audios = ""
        self._similarity_threshold = similarity_threshold
        self.notUnderstand_responses = [
            "I'm sorry, I did not understand that",
            "Please would you repeat that",
            "That may not be in my database",
            "That may not be in my vocabulary",
            "I could not understand that"
        ]

        self.recognizer = Recognizer()

    def _check_compatability(self, sequence: str, to_compare: str) -> float:
        """Check compatability ratio."""
        self._matcher = SequenceMatcher(a=sequence, b=to_compare)
        return self._matcher.ratio()

    def _parse_intents(self) -> dict:
        """Parse the intents into a dictionary."""
        # Just as a separate method in case I need to add more parsing and editing
        self._intents = json.loads(self._intents)
        for tag in self._intents:
            for index, value in enumerate(self._intents[tag]["patterns"]):
                self._intents[tag]["patterns"][index] = "computer " + \
                    value.lower()

        return self._intents

    def _recognize(self) -> None:
        """Recognize data from input."""
        try:
            with Microphone() as mic:
                print("Adjusting...")
                self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                print("Listening...")
                audio = self.recognizer.listen(mic)

                self.input = self.recognizer.recognize_google(audio).lower()

        except UnknownValueError:
            print("Reinitializing...")
            self.recognizer = Recognizer()  # Reinitialize
            try:
                self._recognize()
            except RecursionError:
                tts.speak(
                    "You have not asked me a question in a while. Shutting down.")
                exit()

    def _get_probs(self, pattern: str) -> str:
        """Get the probability of it being any certain string."""
        self._max_tag = "notUnderstand"

        print(pattern)
        self._probabilities = {}
        for key in self._intents:
            self._probabilities[key] = [
                self._check_compatability(item, pattern)
                for item in self._intents[key]["patterns"]
            ]

    def _get_max_prob(self) -> str:
        """Get the maximum probability and its tag."""
        self._max_tag = "notUnderstand"
        self._max_value = self._similarity_threshold
        for key in self._probabilities:
            for item in self._probabilities[key]:
                if item > self._max_value:
                    self._max_value = item
                    self._max_tag = key
        print(self._max_tag)
        return self._max_tag

    def act_functions(self):
        if self._max_tag == "exit":
            tts.speak(random.choice(
                [
                    "Goodbye.",
                    "Shutting down.",
                    "Program terminated.",
                    "See ya later.",
                    "Cheerio."
                ]
            ))
            exit()

    def act_strings(self):
        tts.speak(random.choice(
            self._intents[self._max_tag]["responses"]))

    def act(self):
        if self._max_tag == "notUnderstand":
            tts.speak(random.choice(self.notUnderstand_responses))
        elif self._intents[self._max_tag]["responses"] != []:
            self.act_strings()
        else:
            self.act_functions()

    def run(self) -> None:
        self._parse_intents()
        print("Ready to help!")
        while True:
            self._recognize()
            print(self.input)
            if "computer" in list(self.input.split(" ")):
                self._get_probs(self.input)
                self._get_max_prob()
                self.act()


if __name__ == "__main__":
    print()
    assistant = ComputerAssistant("./Intents/intents.json", 0.5)
    assistant.run()
