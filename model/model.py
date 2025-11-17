from database.impianto_DAO import ImpiantoDAO
from database.consumo_DAO import ConsumoDAO
from datetime import datetime


'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        consumo_medio=[]
        for impianto in self._impianti:
            # prendo i consumi dell'impianto in base al codice impianto
            consumi = impianto.get_consumi()
            # filtro in base al mese
            consumi_mensili=[]
            for consumo in consumi:
                if consumo.data.month==mese:
                #data_consumo=str(consumo.data)
                #parti=data_consumo.split("-")
                #mese_split=int(parti[1])
                #if mese_split==mese:
                    consumi_mensili.append(consumo.kwh)  # mi ritorna una lista con i kwh

            if len(consumi_mensili)==0:
                media=0
            else:
                media= sum(consumi_mensili)/ len(consumi_mensili)

            consumo_medio.append((impianto.nome, media))

        return consumo_medio

        # TODO

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo =-1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)
        costo_ottimo=[0] # metto una lista così il valore puo essere modificato dentro la ricorsione


        self.__ricorsione(self.__sequenza_ottima, 1, None, costo_ottimo, consumi_settimana)
        self.__costo_ottimo=costo_ottimo[0]

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        if giorno>7:
            return
        else:
            costo_minore=0 # tiene il costo migliore dentro al ciclo
            impianto_scelto=None # tiene l'impianto che ha quel costo
            for impianto in consumi_settimana:
                costo_giornaliero=consumi_settimana[impianto][giorno -1]  # per ogni impianto prendo il consumo del giorno
                if impianto!=ultimo_impianto and ultimo_impianto is not None:
                    costo_giornaliero+=5  # se l'impianto non è uguale a quello precedente, aggiungi il costo di 5 euro
                if costo_giornaliero<costo_minore or costo_minore==0:
                    costo_minore=costo_giornaliero
                    impianto_scelto=impianto
            sequenza_parziale.append(impianto_scelto)
            costo_corrente[0]+=costo_minore
            self.__ricorsione(sequenza_parziale, giorno+1, impianto_scelto, costo_corrente, consumi_settimana)

        # TODO

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi_prima_settimana = {}
        for impianto in self._impianti:
            consumi =impianto.get_consumi()
            lista_kwh_giorno = []
            for consumo in consumi:
                #data_consumo = str(consumo.data)
                #parti = data_consumo.split("-")
                #mese_split = int(parti[1])
                #giorno_split=int(parti[2])
                if consumo.data.month==mese and consumo.data.day<=7:
                    lista_kwh_giorno.append(consumo.kwh)
            consumi_prima_settimana[impianto.id] = lista_kwh_giorno
        return consumi_prima_settimana

        # TODO

