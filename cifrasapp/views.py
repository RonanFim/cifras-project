from django.shortcuts import render, get_object_or_404
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
    # chord.changeKey(2)
    return render(request, 'cifrasapp/chords.html', {'chord':chord})
