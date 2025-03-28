from colorfield.fields import ColorField
from django.db import models
from django.conf import settings
from django.utils import timezone

keyMapSus = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
keyMapBem = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']


class Label(models.Model):
    name = models.CharField(max_length=30)
    color = ColorField(format="hexa")

    def __str__(self):
        return self.name


class Chords(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    key = models.CharField(max_length=3)
    content = models.TextField()
    formated_lines = []
    tags = models.ManyToManyField(Label)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    published_date = models.DateTimeField(default=timezone.now)

    def publish(self):
        self.published_date = timezone.now()
        self.formatLines()
        self.save()
    
    def formatLines(self):
        raw_lines = self.content.splitlines()
        # print(raw_lines)
        self.formated_lines = []
        for line in raw_lines:
            pos = line.find("{")
            chords_line = "[c]"
            lyrics_line = "[l]"
            previous_pos = 0
            while pos >= 0:
                pos2 = line.find("}")
                chords_line += " " * (pos - previous_pos)
                chords_line += line[(pos+1):pos2]
                line = line[:pos] + line[(pos2+1):]
                previous_pos = pos + 1
                pos = line.find("{")
            lyrics_line += line
            if(chords_line != "[c]"):
                self.formated_lines.append(chords_line)
            # if(lyrics_line != "[l]"):
            self.formated_lines.append(lyrics_line)
    
    def changeContentChords(self, chordsDict):
        linesIdx = []
        for line in chordsDict:
            if line['chords']:
                linesIdx.append(line['index'])
        newContent = ""
        for idx,line in enumerate(self.content.splitlines(keepends=True)):
            if idx in linesIdx:
                chordsList = [line['chords'] for line in chordsDict if line['index'] == idx]
                lineSearch = line
                for ch in chordsList[0]:
                    pos1 = lineSearch.find("{")
                    pos2 = lineSearch.find("}")
                    newContent += lineSearch[:pos1] + "{" + ch + "}"
                    lineSearch = lineSearch[(pos2+1):]
                newContent += lineSearch
            else:
                newContent += line
        self.content = newContent
        self.formatLines()


    def changeKey(self, interval:int):
        """
        Altera o tom da musica. Recebe como parametro o intervalo em semitons.

        :param interval: int
        """
        if interval == 0:
            return
        changeDict = []
        for idx,line in enumerate(self.content.splitlines()):
            chordsInLine = []
            pos = line.find("{")
            while pos >= 0:
                pos2 = line.find("}")
                chordsInLine.append(line[(pos+1):pos2])
                line = line[:pos] + '~' + line[(pos+1):]
                line = line[:pos2] + '~' + line[(pos2+1):]
                pos = line.find("{")

            newChords = [self.__offsetChord(ch, interval) for ch in chordsInLine]
            changeDict.append({'index': idx, 'chords':newChords})
        self.changeContentChords(changeDict)
        self.key = self.__offsetChord(self.key, interval)
        # self.save()


    def getDistance(self, currKey):
        originalpos = self.__chordPosInList(self.key)
        currentpos = self.__chordPosInList(currKey)
        if (originalpos < 0) or (currentpos < 0):
            return 0
        return (currentpos - originalpos)
        

    def __separateChord(self, chord):
        chPrefix = chord[0]
        chExt = ""
        if len(chord) > 1:
            if chord[1] in ['#', 'b']:
                chPrefix = chord[0:2]
                if len(chord) > 2:
                    chExt = chord[2:]
            else:
                chExt = chord[1:]
        return (chPrefix, chExt)


    def __chordPosInList(self, chord):
        checkChord,_ = self.__separateChord(chord)
        pos = -1
        if checkChord in keyMapSus:
            pos = keyMapSus.index(checkChord)
        elif checkChord in keyMapBem:
            pos = keyMapBem.index(checkChord)
        return pos


    def __offsetChord(self, ch:str, interval:int):
        interval = interval % 12    # evita intervalos maiores que 12 semitons
        chBasic, chExt = self.__separateChord(ch)
        
        if chBasic in keyMapSus:
            offset = keyMapSus.index(chBasic) + interval
            if offset >= 12:
                offset -= 12
            elif offset < 0:
                offset += 12
            newChord = keyMapSus[offset]
        elif chBasic in keyMapBem:
            offset = keyMapBem.index(chBasic) + interval
            if offset >= 12:
                offset -= 12
            elif offset < 0:
                offset += 12
            newChord = keyMapBem[offset]
        return newChord+chExt


    def __str__(self):
        return self.title + " - " + self.artist
