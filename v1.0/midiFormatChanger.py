from mido import MidiFile, MidiTrack, Message, merge_tracks
import csv, math
from threading import Thread
from LoadingRotationBar import LoadingRotationBar
import datetime

caractereNote = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒ"
time_precision = 50

# Fonctions inutiles mais pour tester la lib
def clean_set_tempo(file):
    # 
    # Nettoyer un fichier midi de tous les [set_tempo]
    # 
    midi_source = MidiFile(file)
    midi_target = MidiFile(type=midi_source.type)
    for track in midi_source.tracks:
        track_target = MidiTrack()
        for msg in track:
            if not msg.type == "set_tempo":
                track_target.append(msg)
        if len(track_target) > 0:
            midi_target.tracks.append(track_target)
    midi_target.save(".\\midi_files_target\\test.mid")


def print_detail(file):
    #
    # Affiche les détails de chaque track, sous la forme :
    # Nom de la track
    # Nbr de messages meta
    # Nbr de messages standards
    # Composition de la track
    #
    midi_source = MidiFile(file)
    for i, track in enumerate(midi_source.tracks):
        num_total_msg = len(track)
        num_meta_msg = len([msg for msg in track if msg.is_meta])
        num_normal_msg = len([msg for msg in track if not msg.is_meta])
        print(track.name)
        print(f"Messages meta : {num_meta_msg}")
        print(f"Messages standards : {num_normal_msg}")
        if num_meta_msg == num_total_msg:
            print(f"La track {i} est composée uniquement de messages meta")
        elif num_normal_msg == num_total_msg:
            print(f"La track {i} est composée uniquement de messages standards")
        else:
            print(f"La track {i} est composée à la fois de messages meta et standards")
        print()



# Fonctions pour transférer les données entre les formats de fichiers
def midiToCsv(source, target):
    print(f"Transformation du fichier midi {source} en fichier csv")
    animation = LoadingRotationBar()
    start = datetime.datetime.now()

    midi_source = MidiFile(source)
    midicsv = []
    time_offset = 0
    for msg in merge_tracks(midi_source.tracks):
        if msg.type == "note_on" or msg.type == "note_off":

            msg_csv = []
            msg_csv.append("note_off" if msg.velocity == 0 else msg.type)
            msg_csv.append(msg.note)
            msg_csv.append(msg.channel)
            msg_csv.append(msg.time + time_offset)
            time_offset = 0
            midicsv.append(msg_csv)
        else:
            time_offset += msg.time
    with open(target, "w") as csv_file:
        csv_writer = csv.writer(csv_file, dialect='unix')
        csv_writer.writerows(midicsv)

    end = datetime.datetime.now()
    animation.finish_loading()
    print(f"Transformation terminée en {(end - start).total_seconds()}s.\nFichier csv disponible ici : {target}")


def csvToMidi(source, target):
    print(f"Transformation du fichier csv {source} en fichier midi")
    animation = LoadingRotationBar()
    start = datetime.datetime.now()

    with open(source) as csv_file:
        csv_reader = csv.reader(csv_file, dialect='unix')
        midifile = MidiFile()
        track = MidiTrack()
        for line in csv_reader:
            track.append(Message(line[0], note=int(line[1]), time=int(line[3])))
        midifile.tracks.append(track)
        midifile.save(target)

    end = datetime.datetime.now()
    animation.finish_loading()
    print(f"Transformation terminée en {(end - start).total_seconds()}s.\nFichier midi disponible ici : {target}")


def csvToText(source, target):
    print(f"Transformation du fichier csv {source} en fichier texte")
    animation = LoadingRotationBar()
    start = datetime.datetime.now()

    musiqueTexte = ""
    with open(source) as csv_file:
        csv_reader = csv.reader(csv_file, dialect='unix')
        currentLetters = []
        for line in csv_reader:
            if not int(line[3]) == 0 and not musiqueTexte == "" or currentLetters:
                for i in range(math.ceil(int(line[3]) / time_precision)):
                    # la boucle for peut potentiellement fausser les analyser de l'ia
                    # essayer de l'enlever si jamais l'ia ne ressort qu'une note continue
                    musiqueTexte += "".join(currentLetters) + " "
            # print(line[1])
            char = caractereNote[int(line[1])] # Transformation de la note en caractère ASCII
            if line[0] == "note_on":
                if not char in currentLetters:
                    currentLetters.append(char)
                    currentLetters.sort()
            elif line[0] == "note_off":
                if char in currentLetters:
                    currentLetters.remove(char)
                    currentLetters.sort()
    with open(target, "w", encoding="utf-8") as txt_file:
        txt_file.write(musiqueTexte)

    end = datetime.datetime.now()
    animation.finish_loading()
    print(f"Transformation terminée en {(end - start).total_seconds()}s.\nFichier texte disponible ici : {target}")


def textToCsv(source, target):
    print(f"Transformation du fichier texte {source} en fichier csv")
    animation = LoadingRotationBar()
    start = datetime.datetime.now()

    csv_music = []
    current_notes = []
    with open(source,  encoding="utf-8") as txt_file:
        music = txt_file.readlines()[0].split(" ")
        time_offset = 0
        for notes in music:
            for note in current_notes:
                if not note in notes:
                    # La note vient de se terminer
                    csv_music.append(["note_off", caractereNote.index(note), "1", time_offset])
                    current_notes.remove(note)
                    time_offset = 0
            for note in notes:
                if not note in current_notes:
                    # la note vient de commencer
                    csv_music.append(["note_on", caractereNote.index(note), "1", time_offset])
                    current_notes.append(note)
                    time_offset = 0
            time_offset += time_precision

    with open(target, "w") as csv_file:
        csv_writer = csv.writer(csv_file, dialect='unix')
        csv_writer.writerows(csv_music)

    end = datetime.datetime.now()
    animation.finish_loading()
    print(f"Transformation terminée en {(end - start).total_seconds()}s.\nFichier csv disponible ici : {target}")


if __name__ == "__main__":
    start = datetime.datetime.now()
    # midiToCsv(".\\midi_files_rachmaninov\\rac_op33_8.mid", ".\\midi.csv")
    # print()
    # csvToText(".\\midi.csv", ".\\text_midi_files_rachmaninov\\rac_op33_8.txt")
    # print()
    textToCsv(".\\generated_music.txt", '.\\generated_music.csv')
    print()
    csvToMidi(".\\generated_music.csv", ".\\generated_music.mid")
    end = datetime.datetime.now()
    print()
    print(f"Temps total d'exécution : {(end - start).total_seconds()}")