from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()


    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):

        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):

        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):


        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        relazioni = TourDAO.get_tour_attrazioni()
        for relazione in relazioni:
            id_t = relazione["id_tour"].strip()
            id_a = relazione["id_attrazione"].strip()
            t = self.tour_map.get(id_t)
            a = self.attrazioni_map.get(id_a)
            if t is None:
                print("Tour non trovato:", id_t)
                continue
            if a is None:
                print("Attrazione non trovata:", id_a)
                continue

            t.attrazioni.add(a)
            a.tour.add(t)



    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """

        tours_disponibili = [t for t in self.tour_map.values() if t.id_regione == id_regione]
        if max_giorni is None:
            max_giorni = float("inf")
        if max_budget is None:
            max_budget = float("inf")
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self._ricorsione(
            start_index=0,
            pacchetto_parziale=[],
            durata_corrente=0,
            costo_corrente=0.0,
            valore_corrente=0,
            attrazioni_usate=set(),
            tours_disponibili=tours_disponibili,
            max_giorni=max_giorni,
            max_budget=max_budget
    )
        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set, tours_disponibili, max_giorni: int, max_budget: float):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""
        if start_index >= len(tours_disponibili):
            if valore_corrente > self._valore_ottimo:
                self._valore_ottimo = valore_corrente
                self._pacchetto_ottimo = pacchetto_parziale.copy()
                self._costo = costo_corrente
            return
        tour = tours_disponibili[start_index]
        if (durata_corrente +tour.durata_giorni <= max_giorni and
            costo_corrente +tour.costo <= max_budget):

                nuove_attrazioni = attrazioni_usate.union(tour.attrazioni)
                valore_totale = sum(a.valore_culturale for a in tour.attrazioni if a not in attrazioni_usate)


                pacchetto_parziale.append(tour)
                self._ricorsione(
                    start_index +1,
                    pacchetto_parziale,
                    durata_corrente +tour.durata_giorni,
                    costo_corrente +float(tour.costo),
                    valore_corrente + valore_totale,
                    nuove_attrazioni,
                    tours_disponibili,
                    max_giorni,
                    max_budget)
                pacchetto_parziale.pop()
        #caso in cui escludo il tour
        self._ricorsione(
            start_index + 1,
            pacchetto_parziale,
            durata_corrente,
            costo_corrente,
            valore_corrente,
            attrazioni_usate,
            tours_disponibili,
            max_giorni,
            max_budget
        )


