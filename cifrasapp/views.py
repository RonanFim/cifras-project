from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import redirect
from .models import Chords
# from .forms import PostForm

# request: o que recebemos do usuario pela internet
def home(request):
    chordsList = Chords.objects.all().order_by('title')
    return render(request, 'cifrasapp/home.html', {'chords':chordsList})

def chordsPage(request, pk):
    chord = get_object_or_404(Chords, pk=pk)
    chord.formatLines()
    if request.method == 'POST':
        if 'minusFullTone' in request.POST:
            chord.changeKey(-2)
        elif 'minusHalfTone' in request.POST:
            chord.changeKey(-1)
        elif 'plusHalfTone' in request.POST:
            chord.changeKey(1)
        elif 'plusFullTone' in request.POST:
            chord.changeKey(2)
    return render(request, 'cifrasapp/chords.html', {'chord':chord})

# def changeChordsKey(request, pk, interval):
#     chord = get_object_or_404(Chords, pk=pk)
#     chord.formatLines()
#     chord.changeKey(interval)
#     # chord.save()
#     return render(request, 'cifrasapp/chords.html', {'chord':chord})
