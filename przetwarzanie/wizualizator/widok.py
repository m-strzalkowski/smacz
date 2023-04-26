from datetime import datetime
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from random import randrange
from time import sleep
import sys
from tkinter import simpledialog, filedialog
import re

from zasysacz import nasluch_ssh
from dekoder import DekoderRejestratora
import matplotlib
matplotlib.use('TkAgg')
MAXLEN = 1000
MAXSKIP = 100
#x_data, y_data = [], []
klawisze = {klawisz:podpis for klawisz, podpis in zip(
[x.strip() for x in "t        ,m       , l  , i       , 1  ,2 , 3  ,4 , 5 , 6  ,7  ,8,  9  , ! ,@  ,#  ,$   ,% , ^ , & , * , ( ".strip().split(",")],
[x.strip() for x in "datetime,microsec,label,impulses, pax,pay,paz,pzx,pzy,pzz,pmx,pmy,pmz, bax,bay,baz,bzx,bzy,bzz,bmx,bmy,bmz".strip().split(",")]
)}
G1 = {x:True for x in [x.strip() for x in "pax,pay,paz".strip().split(",")]}
debug = lambda *args, **kwargs:None
debug=print
def odswiez_dane_z_ssh(gen,data,mask,settings):
    MAXLEN,MAXSKIP = settings
    #x_data, y_data = data
    i=0
    for wiersz in gen:
        i+=1
        #print('%%%',wiersz)
        if wiersz:
            wiersz = dekoder.dekoduj_wiersz(wiersz)
            if not wiersz:
                return
            #print('%%*',wiersz)
            #data['T'].append(wiersz['T'])#datetime
            #print(wiersz['T'].__repr__())
            #print(wiersz['T'])
            #print('wiersz:',wiersz)
            #print('mask.items():',mask.items())
            for seria in wiersz:
                #print(f'seria:,nr:{seria}:{wiersz[seria]}')
                if seria not in data:
                    data[seria] = []
                data[seria].append(wiersz[seria])
            if len(data['T']) > MAXLEN:
                for seria in data:
                    data[seria] = data[seria][-MAXLEN:]
                    #data[seria].pop(0)
            # for seria, nrlinii in mask.items():
            #     print('seria:,nr:',seria,nrlinii)
            #     if seria not in data:
            #         data[seria] = []
            #     data[seria].append(float(wiersz[seria]))
            #     if len(x_data) > MAXLEN:
            #         data['T'].pop(0)
            #         data[seria].pop(0)
            #print('mask:,data',mask,data)
            if i>MAXSKIP:
                return
            dl = len(data['T'])
            for seria in data:
                if len(data[seria])!=dl:
                    raise Exception(f'Nie zgadza sie: {dl,len(data[seria]),seria}', )
        else:
            i=0
            return
def ret_update(gen,data,ax,mask,settings):
    #mask - słownik z tym, co rysować
    #x_data, y_data = data
    def update(frame):
        #print('update')
        odswiez_dane_z_ssh(gen,data,mask,settings)
        #print(data)
        #if 'T' not in data:
        #    return None
        x_data = data['T']
        lines = []
        #print('przedfor',ax.lines)
        for seria, nrlinii in mask.items():
            #print(f"seria:{seria} nrlinii{nrlinii}")
            if nrlinii >= len(ax.lines):
                print(f"ERR:{(nrlinii,len(ax.lines)) }")
                continue
            line = ax.lines[nrlinii]
            #print(f"line.set_data{(x_data, data[seria]), len(x_data), len(data[seria])}")
            line.set_data(x_data, data[seria])
            lines.append(line)
        figure.gca().relim()
        figure.gca().autoscale_view()
        #print('/update:',lines)
        return lines #def func(frame, *fargs) -> iterable_of_artists
    return update
def ret_update_random(data):
    x_data,y_data = data
    def update_random(frame):
        x_data.append(datetime.now())
        y_data.append(randrange(0, 100))
        if len(x_data) > MAXLEN:
            x_data.pop(0)
            y_data.pop(0)
        ax.lines[0].set_data(x_data, y_data)
        figure.gca().relim()
        figure.gca().autoscale_view()
        return (ax.lines[0],)
    return update_random
def ret_on_press(ax,data, mask, settings):
    print(mask)
    def on_press(event):
        print('press', event.key)
        sys.stdout.flush()
        k = ""+event.key
        if event.key == 'x':
            #visible = xl.get_visible()
            #xl.set_visible(not visible)
            figure.suptitle('Pressed')
            figure.canvas.draw()
        elif event.key == 'q':
            print(data)
            exit(0)
        elif event.key == 's':
            #save_as = filedialog.asksaveasfilename(title='Zapisz jako')
            pyplot.savefig()
        elif event.key == ',':
            NEWMAXLEN = simpledialog.askinteger('Ustawianie pojemnosci', 'Ile punktów czasowych ma być na wykresie?', minvalue=10, maxvalue=10000)
            if NEWMAXLEN is not None:
                settings[0] = NEWMAXLEN
        elif event.key == 'delete':
            for k in data:
                data[k]=[]
        elif event.key == 'd':
            usuń_z_wykresu(ax,mask,'pay')
        elif event.key == 'a':
            dodaj_do_wykresu(data,ax,mask,'pay')
        elif event.key == 'D':
            for k in list(G1.keys()):
                print('usun '+k)
                usuń_z_wykresu(ax, mask, k)
        elif event.key == 'A':
            for k in list(G1.keys()):
                if k not in ['datetime','miliseconds']:
                    dodaj_do_wykresu(data,ax,mask,k)
        elif event.key == '0':
            wyczysc_wykres(ax,mask)
            #for k in list(mask.keys()):
            #    print('usun '+k)
            #    usuń_z_wykresu(ax, mask, k)
        elif event.key == ')':
            for k in klawisze:
                if klawisze[k] not in ['datetime','miliseconds']:
                    dodaj_do_wykresu(data,ax,mask,klawisze[k])
        elif event.key in ['.','+']:
            if event.key == '.':
                msg = 'Co chcesz wyświetlić?'
                wyczysc_wykres(ax, mask)
            else:
                msg = 'Co chcesz dodać?'
            filtr = simpledialog.askstring('Wpisz wyrażenie regularne.', msg)#, parent=parent)
            print(f"filtr:{filtr}")
            for k in klawisze:
                if re.match(filtr,klawisze[k]) and (filtr == 'datetime' or klawisze[k] != 'datetime'):
                    dodaj_do_wykresu(data,ax,mask,klawisze[k])
        elif k in klawisze:
            print(f"maska:{mask} k:{k}")
            print(f"klawisze[k]:{klawisze[k]}")
            b = int(klawisze[k] in mask)#jeśli jest - usuń, inaczej dodaj
            print('b,k,klawisze[k],mask',b,k,klawisze[k],mask)
            [dodaj_do_wykresu,usuń_z_wykresu][b](*([data,ax,mask,klawisze[k]][b:]))
            print(f"maska':{mask}")
    return on_press
        
def dodaj_do_wykresu(data,ax,mask,label):
    x_data, y_data = data['T'],data[label]
    #data = {'T':xdata, ''}
    #(line,) = pyplot.plot_date('-')
    (line,) = pyplot.plot_date(x_data, y_data, '-',label=label)
    ax.legend(loc='center left', bbox_to_anchor=(1, .5))
    mask[label] = ax.lines.index(line)#len(ax.lines)-1
    #(line,) = pyplot.plot(x_data, y_data, '-')
    #pyplot.gcf().autofmt_xdate()
    return list((line,))
def wyczysc_wykres(ax, mask):
    #ax.lines.remove()
    while len(ax.lines)>0:
        ax.lines.pop(0)
    mask.clear()
    ax.legend(loc='center left', bbox_to_anchor=(1, .5))
def usuń_z_wykresu(ax,mask,label):
    print(f"usuń:{ax.lines, mask[label], ax.lines[mask[label]]}")
    ax.lines.remove(ax.lines[mask[label]])
    del mask[label]
    ax.legend(loc='center left', bbox_to_anchor=(1, .5))

if __name__ == '__main__':
    gen = nasluch_ssh()#start_connection()
    data = {k:[] for k in list(klawisze.values())+['T']}
    mask = {}
    settings = [MAXLEN,MAXSKIP]
    figure = pyplot.figure()
    ax = figure.add_subplot(111)
    
    #ax = figure.axes[0]
    
    figure.autofmt_xdate()
    figure.canvas.mpl_connect('key_press_event', ret_on_press(ax,data,mask,settings))
    figure.suptitle('odczyty z IMów')
    update = ret_update(gen,data,ax,mask,settings)
    dodaj_do_wykresu(data,ax,mask,'pax')
    update(None)
    #ax.legend()
    ax.legend(loc='center left', bbox_to_anchor=(1, .5))
    dekoder = DekoderRejestratora()
    animation = FuncAnimation(figure, update, interval=200)
    #animation = FuncAnimation(figure, ret_update_random([[],[]]), interval=200)
    pyplot.show()

def test():
    dekoder = DekoderRejestratora()
    gen = nasluch_ssh()#start_connection()
    i=0
    for wiersz in gen:
        i+=1
        if i>10:
            exit(0)
        if wiersz:
            dekoder.dekoduj_wiersz(wiersz)
        else:
            sleep(1)
        #print('...',li)
