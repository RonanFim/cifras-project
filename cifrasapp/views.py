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
    id, currentKey = request.session.get('currKey', (-1, chord.key))
    if id != pk:
        currentKey = chord.key
        request.session['currKey'] = (pk, chord.key)
    offsetKey = chord.getDistance(currentKey)
    if request.method == 'POST':
        if 'minusFullTone' in request.POST:
            chord.changeKey(offsetKey - 2)
        elif 'minusHalfTone' in request.POST:
            chord.changeKey(offsetKey - 1)
        elif 'plusHalfTone' in request.POST:
            chord.changeKey(offsetKey + 1)
        elif 'plusFullTone' in request.POST:
            chord.changeKey(offsetKey + 2)
        request.session['currKey'] = (pk, chord.key)
    elif offsetKey != 0:
        chord.changeKey(offsetKey)
    chord.formatLines()
    return render(request, 'cifrasapp/chords.html', {'chord':chord})
