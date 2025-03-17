from colorfield.fields import ColorField
from django.db import models
from django.conf import settings
from django.utils import timezone

class Label(models.Model):
    name = models.CharField(max_length=30)
    # color = models.CharField(max_length=7)
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
    
    def changeKey(self, interval):
        if not self.formated_lines:
            return
        if interval == 0:
            return
        interval = interval % 12    # evita intervalos maiores que 12 semitons
        keyMapSus = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        keyMapBem = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
        print(self.formated_lines)
        for idx,line in enumerate(self.formated_lines):
            if line[0:3] != "[c]":
                continue
            lineChords = line[3:].split()
            for ch in lineChords:
                chExt = ""
                chBasic = ch[0]
                if len(ch) > 1:
                    if (ch[1] == '#') or (ch[1] == 'b'):
                        chBasic = ch[0:1]
                        if len(ch) > 2:
                            chExt = ch[2:]
                    else:
                        chExt = ch[1:]         
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
                self.formated_lines[idx] = line.replace(ch, newChord+chExt)
        print(self.formated_lines)

    
    def __str__(self):
        return self.title + " - " + self.artist
