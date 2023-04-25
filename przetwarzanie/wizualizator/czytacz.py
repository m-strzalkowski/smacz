from datetime import datetime
from dekoder import DekoderRejestratora
class CzytaczPliku:
    wiersze = list()
    aktualny_indeks = None
    fp = None
    MAX_ZLYCH_WIERSZY = 1024
    dekoder = None
    def __init__(self, nazwa_pliku):
        self.fp = open(nazwa_pliku, 'r')
        self.dekoder = DekoderRejestratora()
    def __del__(self):
        self.fp.close()
    def __next__(self) -> dict:#wiersz
        i=0
        while (linia := self.dekoder.dekoduj_wiersz(self.fp.readline())) is None:
            i+=1
            if i>self.MAX_ZLYCH_WIERSZY:
                raise Exception('Dekoder nie może zdekodować pliku!')

    def przestaw_na_pierszy_po(self, godz:datetime):
        pass