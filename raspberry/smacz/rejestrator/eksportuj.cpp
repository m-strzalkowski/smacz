#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include "LSM9DS1_Types.h"
#include "LSM9DS1.h"
#include "rejestrator.h"

FILE * plik_nagrania = NULL;
FILE * plik_stanu = NULL;
int przeczytano = 0;
int zakoncz()
{
    if(plik_nagrania){fclose(plik_nagrania);}
    if(plik_stanu)
    {
        plik_stanu = freopen(NULL, "w", plik_stanu);
        if(!plik_stanu){return EXIT_FAILURE;}
        fprintf(plik_stanu,"%d", przeczytano);
        fclose(plik_stanu);
    }
    return EXIT_SUCCESS;
}
void sig_handler(int sig) {
    switch (sig) {
    case SIGINT:
        fprintf(stderr, "Received SIGINT...\n");
        exit(zakoncz());
    case SIGTERM:
        fprintf(stderr, "Received SIGTERM...\n");
        exit(zakoncz());
    default:
        fprintf(stderr, "wasn't expecting that!\n");
        abort();
    }
}

int czestotliwosc = 20;//Hz
int main(int argc, char *argv[]) {
    bool dalej=false;
    bool csv=true;
    fprintf(stdout,"t_sec,label, pax,pay,paz,pzx,pzy,pzz,pmx,pmy,pmz, bax,bay,baz,bzx,bzy,bzz,bmx,bmy,bmz\n");
    char * sciezka_zapisu = (char *)"dane/zapis";
    char * sciezka_stanu_eksportu_zapisu = (char *)"dane/zapis_pozycja";
    Odczyt odczyt;

    int opt;
    while ((opt = getopt(argc, argv, "ch")) != -1) {
        switch (opt) {
        case 'c': dalej = true; break;
        case 'h': csv = false; break;
        default:
            fprintf(stderr, "Usage: %s [-c -h] [input file]\n", argv[0]);
            exit(EXIT_FAILURE);
        }
    }
    if(optind < argc)
    {
        sciezka_zapisu = argv[optind];
    }

    plik_nagrania = fopen(sciezka_zapisu, "rb");
    if(!plik_nagrania) {plik_nagrania = fopen(sciezka_zapisu, "a+");}
    if(!plik_nagrania)
    {
        fprintf(stderr, "Blad otwierania pliku z zapisem: %s", sciezka_zapisu);
        exit(EXIT_FAILURE);
    }

    plik_stanu = fopen(sciezka_stanu_eksportu_zapisu, "a+");
    fseek(plik_stanu, 0,SEEK_SET);
    if(plik_stanu)
    { 
        if(fscanf(plik_stanu,"%d",&przeczytano))
        {
            if(fseek(plik_nagrania, przeczytano, SEEK_SET) == 0)
            {
                fprintf(stderr, "Przesunieto na pozycje %d, ktora byla zapisana w pliku %s", przeczytano,sciezka_stanu_eksportu_zapisu);
            }
            else{
                fprintf(stderr, "Blad: Przesuniecie na pozycje %d, ktora byla zapisana w pliku %s sie nie udalo.", przeczytano,sciezka_stanu_eksportu_zapisu);
                przeczytano=0; fseek(plik_nagrania, 0,SEEK_SET); fprintf(stderr,"zaczynanie od poczatku\n");
                }
        }else{
            przeczytano=0; fseek(plik_nagrania, 0,SEEK_SET); fprintf(stderr,"zaczynanie od poczatku\n");
        }
        
    }else{
        fprintf(stderr, "Blad otwierania pliku z pozycja do ktorej dotarl eksport ostatnim razem. %s\n", sciezka_zapisu);
        przeczytano=0; fseek(plik_nagrania, 0,SEEK_SET); fprintf(stderr,"zaczynanie od poczatku\n");
    }

    signal(SIGTERM,sig_handler);
    signal(SIGINT,sig_handler);//zalozenie pulapki na ctrl+c 

    int status, status_wiersza;//ile przeczytano pojedynczym read i ile z danego wiersza(o dugoci struktury Odczyt).
    for (;;) {
        
	//chcemy przeczytac dokladnie sizeof(odczyt) bajtow, nie wiecej, nie mniej
        status_wiersza=0;
	    do{
            //fprintf(stderr,"*FR*");
            status = fread(&odczyt, 1,sizeof(odczyt)-status_wiersza,plik_nagrania);
	        //fprintf(stderr, "[%d]\n",status);
            if(status < (int)(sizeof(odczyt)))
            {
                if(feof(plik_nagrania) && status ==0)
                {
                    if(status == 0){fprintf(stderr, "eof\n"); break;}
                //    else{fprintf(stderr, "file corrupted: it has to be divisible into %d byte blocks.", sizeof(odczyt)); exit(EXIT_FAILURE);}
                }
                if(status<=0)
                {
                    fprintf(stderr, "0 bytes read\n");
                    usleep(1000000/20);
                }
                else{
                    status_wiersza +=status;
                    fprintf(stderr, " %d/%d bytes read\n", status_wiersza, sizeof(odczyt));
                }
            }
            else{status_wiersza +=status;}
        }while(status_wiersza<(int)(sizeof(odczyt)));
        //printf("\nST:%d\n",status_wiersza);
	    przeczytano += status_wiersza;//sizeof(odczyt);
        
        if(feof(plik_nagrania))//plik sie skonczyl
        {
            if(!dalej)
            {
                fprintf(stderr, "koniec");
                exit(zakoncz());
            }
            else{
                fprintf(stderr,"\n!waiting (%ld)...!\n",ftell(plik_nagrania));
                usleep(1000000/20);//powinno byc poll(...)
		        //fclose(plik_nagrania);
                plik_nagrania = freopen(NULL, "r", plik_nagrania);//probojemy otworzyc ponownie plik.
                if(!plik_nagrania){fprintf(stderr,"nie udalo sie ponownie otworzyc pliku z zapisem."); zakoncz(); exit(EXIT_FAILURE);}
                if(fseek(plik_nagrania, przeczytano, SEEK_SET) == 0)
                {
                    fprintf(stderr, "Przesunieto na pozycje %d, ktora byla zapisana w pliku %s", przeczytano,sciezka_stanu_eksportu_zapisu);
                 }
                else{
                    fprintf(stderr, "Blad: Przesuniecie na pozycje %d w pliku %s po jego ponownym otwarciu sie nie udalo.Konczenie.\n", przeczytano,sciezka_stanu_eksportu_zapisu);
                    zakoncz(); exit(EXIT_FAILURE);
                }
		        continue;//nie chcemy wypisywac tego samego wiersza danych na wyjscie
            }
        }
/*	if(feof(zapis) && !dalej)
	{
                fprintf(stderr, "koniec");
                exit(zakoncz());
	}*/
        wypisz_odczyt(stdout,&odczyt,csv);

    }

    exit(EXIT_SUCCESS);
}
