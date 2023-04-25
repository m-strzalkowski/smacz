from datetime import datetime
import re
#datetime.strptime('%a %b %d %H:%M:%S %Y,%f', 'Thu Apr 20 23:44:57 2023,480584')
class DekoderRejestratora:
    pola = None
    typy_pól = {'T':lambda x:x,'datetime':str,'microsec':int,'label':int,'impulses':int }#reszta float
    #pola_str = None
    #pola_float = None
    #pola_int = None
    def kolumny(self, wiersz):
        return [ k.strip() for k in wiersz.strip().split(",")]
    def konwertuj_typy_kolumn(self,wiersz:dict):
        w = {}
        for kol, wart in wiersz.items():
            if kol in self.typy_pól:
                typ = self.typy_pól[kol]
            else:
                typ = float
            #print(f"{kol}:typ,wart:{typ,wart}")
            #print(f" typ(wart):{typ(wart)}")
            w[kol] = typ(wart)
        #print(f"wiersz:{w}")
        return w
    def dekoduj_wiersz(self,wiersz):
        #print('===',wiersz)
        wiersz = wiersz.strip()
        if not self.pola:
            if re.match(r"^datetime.*",wiersz):
                self.pola = self.kolumny(wiersz)
                print('pola:',self.pola)
            return None
        else:#pola juz rozpoznane:
            #print('=++',self.kolumny(wiersz))
            wynik = {k:w for k,w in zip(self.pola, self.kolumny(wiersz))}
            wynik['T'] = datetime.strptime(wynik['datetime']+','+wynik['microsec'],'%a %b %d %H:%M:%S %Y,%f')# 'Thu Apr 20 23:44:57 2023,480584')
            wynik = self.konwertuj_typy_kolumn(wynik)
            #print('*++', wynik)
            return wynik

