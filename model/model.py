from database.impianto_DAO import ImpiantoDAO
from database.consumo_DAO import ConsumoDAO

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
            consumi = ConsumoDAO.get_consumi(impianto.id)
            # filtro in base al mese
            consumi_mensili=[]
            for consumo in consumi:
                data_consumo=str(consumo.data)
                parti=data_consumo.split("-")
                mese=int(parti[1])
                if mese==mese:
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
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        print(f"{ costo_corrente }, {sequenza_parziale }")
        if giorno>7:
            if self.__costo_ottimo is None or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima=sequenza_parziale
            return
        else:
            for impianto in consumi_settimana.keys():
                consumo_giornaliero=0

                if (giorno-1) < len(consumi_settimana[impianto]):
                    consumo_giornaliero=consumi_settimana[impianto][giorno-1]

                costo_giornaliero=consumo_giornaliero

                if ultimo_impianto is not None and ultimo_impianto != impianto:
                    costo_giornaliero += 5

                sequenza_parziale.append(impianto)
                self.__ricorsione(sequenza_parziale, giorno + 1, impianto, costo_corrente + costo_giornaliero,consumi_settimana)
                sequenza_parziale.pop()

        # TODO

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi_prima_settimana = {}
        for impianto in self._impianti:
            consumi = ConsumoDAO.get_consumi(impianto.id)
            lista_kwh_giorno = []
            for consumo in consumi:
                data_consumo = str(consumo.data)
                parti = data_consumo.split("-")
                mese_split = int(parti[1])
                giorno_split=int(parti[2])
                if mese_split==mese and 1<=giorno_split<=7:
                        lista_kwh_giorno.append(consumo.kwh)
            consumi_prima_settimana[impianto.nome] = lista_kwh_giorno
        return consumi_prima_settimana

        # TODO

