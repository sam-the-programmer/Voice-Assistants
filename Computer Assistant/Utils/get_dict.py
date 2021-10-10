import json
import g2p_en as g2p

with open("../Intents/intents.json") as file:
    intents = json.load(file)

G2P = g2p.G2p()
words = []
for tag in intents.values():
    for pattern in tag["patterns"]:
        for word in pattern.split(" "):
            words.append(word.lower() + " " + " ".join(G2P(word.lower())))

words = sorted(list(set(words)))


with open("../dictionary.dict", "w") as file:
    file.write("\n".join(words))