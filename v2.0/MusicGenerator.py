import csv
import datetime
import json
import random
import mido
import math

from mido.midifiles.midifiles import MidiFile

from LoadingRotationBar import LoadingRotationBar


class Serializable():
    def importFile(self, file: str) -> None:
        pass

    def exportFile(self, file: str) -> None:
        pass

# Rendre accessible aux premières classes celle déclarées plus tard
class MusicCSV():
    pass
class MusicText():
    pass

class MusicMidi(Serializable):
    def __init__(self, midi: mido.MidiFile = None) -> None:
        super().__init__()
        if not midi == None:
            self.midi_file = midi
            mido.merge_tracks(self.midi_file)

    def importFile(self, file: str) -> None:
        track = mido.merge_tracks(mido.MidiFile(file).tracks)
        self.midi_file = mido.MidiFile()
        self.midi_file.tracks.append(track)

    def exportFile(self, file: str) -> None:
        self.midi_file.save(file)

    def getTrack(self) -> mido.MidiTrack:
        return self.midi_file.tracks[0]

    def parseCSV(self, musicCsv: MusicCSV) -> None:
        print(f"Transformation du csv vers midi")
        animation = LoadingRotationBar()
        start = datetime.datetime.now()

        self.midi_file = mido.MidiFile()
        track = mido.MidiTrack()
        for line in musicCsv.music_csv:
            track.append(mido.Message(line[0], note=int(line[1]), time=int(line[3])))
        self.midi_file.tracks.append(track)

        end = datetime.datetime.now()
        animation.finish_loading()
        print(f"Transformation terminée en {(end - start).total_seconds()}s")
        return self


class MusicCSV(Serializable):
    def __init__(self, csv_list: list[list[str]] = None) -> None:
        super().__init__()
        if not csv_list == None:
            self.music_csv = csv_list

    def importFile(self, file: str) -> None:
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, dialect='unix')
            self.music_csv = list(csv_reader)

    def exportFile(self, file: str) -> None:
        with open(file, "w") as csv_file:
            csv_writer = csv.writer(csv_file, dialect='unix')
            csv_writer.writerows(self.music_csv)

    def parseMidi(self, music_midi: MusicMidi) -> None:
        print(f"Transformation du midi en csv")
        animation = LoadingRotationBar()
        start = datetime.datetime.now()
        self.music_csv = []
        time_offset = 0
        for msg in music_midi.getTrack():
            if msg.type == "note_on" or msg.type == "note_off":
                msg_csv = []
                msg_csv.append("note_off" if msg.velocity == 0 else msg.type)
                msg_csv.append(msg.note)
                msg_csv.append(msg.channel)
                msg_csv.append(msg.time + time_offset)
                time_offset = 0
                self.music_csv.append(msg_csv)
            else:
                time_offset += msg.time
        end = datetime.datetime.now()
        animation.finish_loading()
        print(f"Transformation terminée en {(end - start).total_seconds()}s")
        return self

    def parseText(self, music_text: MusicText) -> None:
        print(f"Transformation du texte en csv")
        animation = LoadingRotationBar()
        start = datetime.datetime.now()

        self.music_csv = []
        current_notes = []
        music = music_text.music_text.split(" ")
        time_offset = 0
        for notes in music:
            for note in current_notes:
                if not note in notes:
                    # La note vient de se terminer
                    self.music_csv.append(["note_off", MusicText.caractereNote.index(note), "1", time_offset])
                    current_notes.remove(note)
                    time_offset = 0
            for note in notes:
                if not note in current_notes:
                    # la note vient de commencer
                    self.music_csv.append(["note_on", MusicText.caractereNote.index(note), "1", time_offset])
                    current_notes.append(note)
                    time_offset = 0
            time_offset += music_text.time_precision

        end = datetime.datetime.now()
        animation.finish_loading()
        print(f"Transformation terminée en {(end - start).total_seconds()}s")
        return self


class MusicText(Serializable):
    caractereNote = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒ"

    def __init__(self, text: str = None, time_precision: int = 50) -> None:
        super().__init__()
        self.time_precision = time_precision
        if not text == None:
            self.music_text = text

    def importFile(self, file: str) -> None:
        with open(file, encoding="utf-8") as txt_file:
            self.music_text = txt_file.readlines()[0]

    def exportFile(self, file: str) -> None:
        with open(file, "w", encoding="utf-8") as txt_file:
            txt_file.write(self.music_text)

    def parseCSV(self, music_csv: MusicCSV) -> None:
        print(f"Transformation du csv en texte")
        animation = LoadingRotationBar()
        start = datetime.datetime.now()
        self.music_text = ""
        currentLetters = []
        for line in music_csv.music_csv:
            if not int(line[3]) == 0 and not self.music_text == "" or currentLetters:
                for i in range(math.ceil(int(line[3]) / self.time_precision)):
                    # la boucle for peut potentiellement fausser les analyser de l'ia
                    # essayer de l'enlever si jamais l'ia ne ressort qu'une note continue
                    self.music_text += "".join(currentLetters) + " "
            char = MusicText.caractereNote[int(line[1])] # Transformation de la note en caractère ASCII
            if line[0] == "note_on":
                if not char in currentLetters:
                    currentLetters.append(char)
                    currentLetters.sort()
            elif line[0] == "note_off":
                if char in currentLetters:
                    currentLetters.remove(char)
                    currentLetters.sort()
        end = datetime.datetime.now()
        animation.finish_loading()
        print(f"Transformation terminée en {(end - start).total_seconds()}s")
        return self


class FrequenceEnchainement(Serializable):
    def __init__(self, freq: dict = dict(), nb_notes_prec: int = 3) -> None:
        super().__init__()
        self.freq = freq
        self.nb_note_prec = nb_notes_prec
        self.time_precision = 50

    def notes(self) -> list[str]:
        return list(self.freq.keys())

    def importFile(self, file: str) -> None:
        with open(file) as json_file:
            self.freq = json.load(json_file)

    def exportFile(self, file: str) -> None:
        with open(file, "w") as json_file:
            json.dump(self.freq, json_file)

    def analyseText(self, text: MusicText) -> None:
        if self.freq == {}:
            self.time_precision = text.time_precision
        elif not self.time_precision == text.time_precision:
            raise ValueError("La précision de la musique doit être la même que les musiques déjà analysées")

        print("Démarrage de l'analyse des fréquences")
        animation = LoadingRotationBar()
        start = datetime.datetime.now()
        music = text.music_text.split(" ")
        notes_precedente = music[:self.nb_note_prec]
        for note_n in music[self.nb_note_prec:]:
            frequences_couple = self.freq.get(" ".join(notes_precedente))
            if frequences_couple:
                frequence_note = self.freq[" ".join(notes_precedente)].get(note_n)
                if frequence_note:
                    self.freq[" ".join(notes_precedente)][note_n] += 1
                else:
                    self.freq[" ".join(notes_precedente)][note_n] = 1
            else:
                self.freq[" ".join(notes_precedente)] = dict()
                self.freq[" ".join(notes_precedente)][note_n] = 1
            notes_precedente.pop(0)
            notes_precedente.append(note_n)
        end = datetime.datetime.now()
        animation.finish_loading()
        print(f"Analyse des fréquences terminée en {(end - start).total_seconds()}")

    def analyseMultipleTexts(self, texts: list[MusicText]) -> None:
        for text in texts:
            self.analyseText(text)


class MusicGenerator():
    def __init__(self, freq: FrequenceEnchainement) -> None:
        self.freq = freq
        self.music = MusicText()

    def generateMusic(self, nb_notes: int = 1000) -> None:
        print("Démarrage de la génération d'une musique")
        animation = LoadingRotationBar()
        start = datetime.datetime.now()
        list_of_existing_notes = self.freq.notes()
        notes_precedentes = list_of_existing_notes[random.randint(0, len(list_of_existing_notes)-1)].split(" ")
        music = " ".join(notes_precedentes)
        frequences_couples = self.freq.freq[" ".join(notes_precedentes)]
        for i in range(nb_notes - self.freq.nb_note_prec):
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
            key = " ".join(notes_precedentes)
            try:
                frequences_couples = self.freq.freq[key]
            except Exception:
                # Les notes précedemment générées sont en dernière position 
                # du fichier analyser et n'apparaissent que là
                # On ne peut donc pas faire de prédiction sur ces notes là
                pass
        end = datetime.datetime.now()
        animation.finish_loading()
        print(f"Génération de la musique terminée en {(end - start).total_seconds()}")
        self.music = MusicText(music)



def miditotext(midi_file) -> MusicText:
    midi = MusicMidi()
    midi.importFile(midi_file)
    csv_music = MusicCSV()
    csv_music.parseMidi(midi)
    music = MusicText()
    music.parseCSV(csv_music)
    return music



if __name__ == "__main__":
    music = miditotext("midi_files_target\\Sonate_01_generated.mid")

    freq = FrequenceEnchainement()
    freq.analyseText(music)

    generator = MusicGenerator(freq)
    generator.generateMusic(10000)
    gen_music = generator.music
    gen_csv = MusicCSV()
    gen_csv.parseText(gen_music)
    gen_midi = MusicMidi()
    gen_midi.parseCSV(gen_csv)
    gen_midi.exportFile("test.mid")