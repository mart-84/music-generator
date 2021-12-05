import datetime
import json
from LoadingRotationBar import LoadingRotationBar
import random


def generate_music(longueur: int):
    print("Démarrage de la génération d'une musique")
    animation = LoadingRotationBar()
    start = datetime.datetime.now()
    # constantes
    data_file = "frequences_notes.json"
    # nombre_notes_precedentes = 3
    generated_file = "generated_music.txt"

    frequences_precedentes = dict()
    with open(data_file) as json_file:
        frequences_precedentes = json.load(json_file)

    list_of_existing_notes = list(frequences_precedentes.keys())
    notes_precedentes = list_of_existing_notes[random.randint(0, len(list_of_existing_notes)-1)].split(" ")
    music = " ".join(notes_precedentes)

    frequences_couples = frequences_precedentes[" ".join(notes_precedentes)]
    for i in range(longueur):
        sum_frequences = sum(frequences_couples.values())
        inote = random.randint(0, sum_frequences)
        
        note_n = list(frequences_couples.keys())[0]
        ecc = frequences_couples[note_n] # effectif cumulé croissant
        j = 0
        while ecc < inote:
            j += 1
            note_n = list(frequences_couples.keys())[j]
            ecc += frequences_couples[note_n]
                
        music += " " + note_n
        notes_precedentes.pop(0)
        notes_precedentes.append(note_n)
        frequences_couples = frequences_precedentes[" ".join(notes_precedentes)]

    
    end = datetime.datetime.now()
    animation.finish_loading()

    with open(generated_file, "w") as g_file:
        g_file.write(music)

    print(f"Génération de la musique terminée en {(end - start).total_seconds()}")


if __name__ == "__main__":
    generate_music(10000)
