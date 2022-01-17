import json
import random
import time
from difflib import SequenceMatcher
from typing import Callable, Tuple, Union

import speech_recognition as sr
import text_to_speech as tts


# ==================== CONSTANTS ==================== #

PREFIXES = ("computer", "peter") # since it mistakes computer for peter sometimes (that may just be because I have a small laptop mic)

# =================================================== #

def recognize(recognizer) -> str:
	try:
		with sr.Microphone() as mic:
			print("[ Functional ]\tAdjusting...", end="")
			recognizer.adjust_for_ambient_noise(mic, duration=0.5)
			print("\r[ Functional ]\tListening...")
			audio = recognizer.listen(mic)

			voice_input = recognizer.recognize_google(audio).lower()
			print(voice_input)

	except sr.UnknownValueError:
		print("Reinitializing...")
		recognizer = sr.Recognizer()  # Reinitialize
		try:
			recognize(recognizer)
		except RecursionError:
			tts.speak("You have not asked me a question in a while. Shutting down.")
			exit()
	
	return voice_input


class Responses(object):
	@staticmethod
	def end() -> None:
		tts.speak(random.choice([
			"Bye.",
			"See you later.",
			"Ok, shutting down.",
			"Goodbye"
		]))

		exit()

	@staticmethod
	def isTime() -> None:
		tts.speak(random.choice([
			"The time is",
			"It is",
			"It's"
		]) + time.strftime(" %I %M %p")) # starting whitespace is needed to stop time blurring into the prefix phrases in the lines above

	@staticmethod
	def addTodo(recognizer, set_memory: Callable, memory) -> None:
		tts.speak(random.choice([
			"What should be added?",
			"What should I add?"
		]))

		voice_input = recognize(recognizer)
		memory["storage"]["todo"].append(voice_input)
		set_memory()
		
		tts.speak(f"Added {voice_input} to your to do list.")

	@staticmethod
	def endTodo(recognizer, set_memory: Callable, memory) -> None:
		tts.speak(random.choice([
			"What should be removed?",
			"What should I delete?",
			"Which item should I delete?"
		]))

		voice_input = recognize(recognizer)
		if voice_input in memory["storage"]["todo"]:
			memory["storage"]["todo"].remove(voice_input)
			return None
		
		ratios = [SequenceMatcher(a=a, b=voice_input).ratio() for a in memory["storage"]["todo"]]
		most_likely = memory["storage"]["todo"][ratios.index(max(ratios))]

		tts.speak(random.choice([
			"Did you mean",
		]) + f" {most_likely}")

		voice_input = recognize(recognizer)
		if SequenceMatcher(a=voice_input, b="yes").ratio() > 0.6:
			memory["storage"]["todo"].remove(most_likely)
		else:
			tts.speak("Cancelling remove.")
		
		set_memory()



class Assistant(object):
	def __init__(self) -> None:
		self.recognizer = sr.Recognizer()

		with open("./intents.json", "r") as file:
			self.intents = json.load(file)
		
		with open("./memory.json", "r") as file:
			self.memory = json.load(file)
	
	def set_memory(self) -> None:
		with open("./memory.json", "r") as file:
			json.dump(self.memory, file)

	@staticmethod
	def _compare(a: str, b: str) -> float:
		return SequenceMatcher(a=a, b=b).ratio()

	def _choose(self, speech) -> Union[str, Callable]:
		choice = ("unknown", 0)

		for k, v in self.intents["intents"].items():

			for pattern in v["patterns"]:
				ratio = self._compare(pattern, speech)
				if ratio > choice[1]:
					choice = (k, ratio)

		return choice[0]

	def _respond(self, choice) -> None:
		if choice == "unknown":
			tts.speak(random.choice(self.intents["unknown_responses"]))

		elif self.intents["intents"][choice]["isFunc"]:
			args = [getattr(self, arg) for arg in self.intents["intents"][choice]["args"]]

			getattr(Responses, choice)(*args)

		else:
			tts.speak(random.choice(self.intents["intents"][choice]["responses"]))

	def _recognize(self) -> str:
		try:
			with sr.Microphone() as mic:
				print("[ Command ]\tAdjusting...", end="")
				self.recognizer.adjust_for_ambient_noise(mic, duration=0.5)
				print("\r[ Command ]\tListening...")
				audio = self.recognizer.listen(mic)

				self.input = self.recognizer.recognize_google(audio).lower()
				print(self.input)

		except sr.UnknownValueError:
			print("[ Command ]\tReinitializing...")
			self.recognizer = sr.Recognizer()  # Reinitialize
			try:
				self._recognize()
			except RecursionError:
				tts.speak("You have not asked me a question in a while. Shutting down.")
				exit()

		return self.input
	
	def _process_prefixes(self, voice_input: str, prefixes: Tuple[str]) -> str:
		for prefix in prefixes:
			if voice_input.startswith(prefix):
				voice_input = voice_input.removeprefix(prefix)

		return voice_input

	def assist(self) -> None:
		while True:
			voice_input = self._recognize()
			if voice_input.strip().startswith(PREFIXES):
				
				choice = self._choose(voice_input.strip())
				self._respond(choice)


def main():
	assistant = Assistant()
	assistant.assist()


if __name__ == "__main__":
	main()
