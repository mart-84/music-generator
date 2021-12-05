import datetime
import json
from LoadingRotationBar import LoadingRotationBar


def merge_files(file_list: list, merge_file: str):
    with open(merge_file, "w") as mixed_file:
        for file in file_list:
            with open(file) as input_file:
                mixed_file.write(input_file.read())
                mixed_file.write(" ")


def analyse_frequence(file_list: list):
    print("Démarrage de l'analyse des fréquences")
    animation = LoadingRotationBar()
    start = datetime.datetime.now()
    # constantes
    merge_file = "mix.txt"
    data_file = "frequences_notes.json"
    nombre_notes_precedentes = 3
    
    frequences_precedentes = dict()

    # Fusion des fichiers pour une analyse plus simple
    merge_files(file_list, merge_file)

    with open(merge_file) as music_file:
        music = music_file.read().split(" ")

        # obtenir les x premieres notes et les mettre dans known_notes
        notes_precedente = music[:nombre_notes_precedentes]

        # lire toutes les autres notes sauf les 2 premieres
        for note_n in music[nombre_notes_precedentes:]:
            
            frequences_couple = frequences_precedentes.get(" ".join(notes_precedente))
            if frequences_couple: # si le couple (N-2, N-1) existe déjà
                frequence_note = frequences_precedentes[" ".join(notes_precedente)].get(note_n)

                if frequence_note: # si la note N existe déjà pour le couple (N-2, N-1)
                    # on incrémente le compte
                    frequences_precedentes[" ".join(notes_precedente)][note_n] += 1
                else:
                    # on ajoute la clé et on met à 1
                    frequences_precedentes[" ".join(notes_precedente)][note_n] = 1

            else: # si le couple (N-2, N-1) n'existe pas
                # on ajoute le couple
                frequences_precedentes[" ".join(notes_precedente)] = dict()
                # on ajoute la note pour le couple et on met à 1
                frequences_precedentes[" ".join(notes_precedente)][note_n] = 1

            # décaler la lecture des notes
            notes_precedente.pop(0)
            notes_precedente.append(note_n)
    
    with open(data_file, "w") as json_file:
        json.dump(frequences_precedentes, json_file)

    end = datetime.datetime.now()
    animation.finish_loading()
    print(f"Analyse des fréquences terminée en {(end - start).total_seconds()}")


if __name__ == "__main__":
    analyse_frequence(
        [
            "text_midi_files_rachmaninov\\rac_op3_2.txt",
            "text_midi_files_rachmaninov\\rac_op23_2.txt",
            "text_midi_files_rachmaninov\\rac_op23_3.txt",
            "text_midi_files_rachmaninov\\rac_op23_5.txt",
            "text_midi_files_rachmaninov\\rac_op23_7.txt",
            "text_midi_files_rachmaninov\\rac_op32_1.txt",
            "text_midi_files_rachmaninov\\rac_op32_13.txt",
            "text_midi_files_rachmaninov\\rac_op33_5.txt",
            "text_midi_files_rachmaninov\\rac_op33_6.txt",
            "text_midi_files_rachmaninov\\rac_op33_8.txt",
        ]
    )
