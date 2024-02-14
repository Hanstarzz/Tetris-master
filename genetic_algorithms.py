

from tetris import TetrisApp
from ai import AI
from random import randrange, randint
import random
import sys
from enum import Enum

class SelectionMethod(Enum):
	roulette = 1

class CrossoverMethod(Enum):
	random_attributes = 1  # Metodo di crossover: scegli attributi casualmente dai genitori.
	average_attributes = 2  # Metodo di crossover: calcola la media degli attributi dai genitori.



POPOLAZIONE = 20  # Numero totale di cromosomi (agenti AI) nella popolazione.
PARTITE_DA_GIOCARE = 2  # Numero di partite che ogni cromosoma deve giocare prima di calcolare la media dei punteggi.
SOPRAVISSUTI = 6  # Numero di cromosomi che sopravvivono attraverso la selezione per ciascuna generazione.
NUOVI_INDIVIDUI = POPOLAZIONE - SOPRAVISSUTI  # Numero di nuovi cromosomi generati in ogni generazione.
SELECTION_METHOD = SelectionMethod.roulette  # Metodo di selezione utilizzato (in questo caso, roulette).
CROSSOVER_METHOD = CrossoverMethod.random_attributes  # Metodo di crossover utilizzato (in questo caso, attributi casuali).
MUTAZIONI = 3  # Numero di passaggi di mutazione per ciascun cromosoma durante la generazione.
TASSO_MUTAZIONE = 20  # Probabilità di mutazione per un dato cromosoma, calcolata come MUTAZIONI / TASSO_MUTAZIONE.
CONVERGED_THRESHOLD = 15  # Soglia di convergenza per determinare se la popolazione ha raggiunto un punto stabile.

def __generate_name():
	current_name = 1
	while True:
		yield current_name
		current_name += 1
_generate_name = __generate_name()

class Individuo(object):
	def __init__(self, euristiche):
		self.name = next(_generate_name)
		self.euristiche = euristiche  # Assegna le euristiche fornite al cromosoma.
		self.total_fitness = 0  # Inizializza la somma totale del fitness del cromosoma a 0.
		self.games = 0  # Inizializza il numero di partite giocate dal cromosoma a 0.

	def avg_fitness(self):
		return self.total_fitness / self.games


class GeneticAlgorithms(object):
	def __init__(self):
		self.app = TetrisApp(self)  # Inizializza l'applicazione Tetris.
		self.ai = AI(self.app)  # Inizializza l'agente AI associato all'applicazione.
		self.app.ai = self.ai  # Collega l'agente AI all'applicazione.
		self.Popolazione = [self.random_individuo() for _ in range(POPOLAZIONE)]  # Genera una popolazione iniziale di cromosomi casuali.
		self.current_individuo = 0  # Inizializza l'indice del cromosoma corrente a 0.
		self.current_generazione = 1  # Inizializza il contatore della generazione corrente a 1.
		self.ai.euristiche = self.Popolazione[
			self.current_individuo].euristiche # Imposta le euristiche dell'agente AI con quelle del cromosoma corrente.

	def run(self):
		self.app.run()

	def next_ai(self):
		self.current_individuo += 1  # Passa al cromosoma successivo nella popolazione.
		if self.current_individuo >= POPOLAZIONE:  # Se si è raggiunto l'ultimo cromosoma, ricomincia da quello iniziale e passa alla prossima generazione.
			self.current_individuo = 0
			self.next_generation()  # Chiamata alla funzione per gestire la transizione alla prossima generazione.
		self.ai.euristica = self.Popolazione[
			self.current_individuo].euristiche  # Imposta le euristiche dell'agente AI con quelle del cromosoma corrente.

	def on_game_over(self, score):
		chromosome = self.Popolazione[self.current_individuo]  # Ottiene il cromosoma corrente.
		chromosome.games += 1  # Incrementa il numero di partite giocate dal cromosoma.
		chromosome.total_fitness += score  # Aggiorna il fitness totale del cromosoma con il punteggio ottenuto.
		if chromosome.games % PARTITE_DA_GIOCARE == 0:  # Se il numero di partite giocate dal cromosoma raggiunge la soglia, passa al cromosoma successivo.
			self.next_ai()
		self.app.start_game()  # Avvia una nuova partita nell'applicazione Tetris.

	def population_has_converged(self):
		t = CONVERGED_THRESHOLD  # Imposta la soglia di convergenza.
		pop = self.Popolazione  # Ottiene la popolazione corrente.
		# Verifica se tutte le euristiche di tutti i cromosomi sono entro la soglia di convergenza rispetto al primo cromosoma.
		return all(
			all(pop[0].euristiche[f] - t < w < pop[0].euristiche[f] + t for f, w in c.euristiche.items()) for c in pop)

	def next_generation(self):
		print("__________________\n")
		# Verifica se la popolazione ha convergito; in caso affermativo, stampa informazioni e termina il programma.
		if self.population_has_converged():
			print("Popolazione has converged on generation %s.\n values: %s"
				% (self.current_generazione, [(f.__name__, w) for f, w in self.Popolazione[0].euristiche.items()]))
			sys.exit()
		print("GENERATION %s COMPLETE" % self.current_generazione)

		# Stampa la media del fitness nella popolazione attuale.
		print("AVG FITNESS", sum([c.avg_fitness() for c in self.Popolazione]) / POPOLAZIONE)
		self.current_generazione += 1

		# Stampa informazioni sui singoli cromosomi nella popolazione attuale.
		for c in self.Popolazione:
			print("chromosome", c.name, "fitness", c.avg_fitness())

		# Trova il cromosoma con il fitness massimo nella popolazione attuale.
		best_chromosome = max(self.Popolazione, key=lambda c: c.avg_fitness())
		print("Fittest chromosome:", best_chromosome.name, "fitness", best_chromosome.avg_fitness(), "\n%s" % [(f.__name__, w) for f, w in best_chromosome.euristiche.items()])

		print("\nEVOLUTION")

		# Seleziona i cromosomi sopravvissuti dalla popolazione attuale.
		nuova_popolazione = self.selection(SOPRAVISSUTI, SELECTION_METHOD)
		for c in nuova_popolazione:
			print("chromosome", c.name, "fitness", c.avg_fitness(), "SURVIVED")

		# Genera nuovi cromosomi attraverso il crossover.
		for _ in range(NUOVI_INDIVIDUI):
			parents = self.selection(2, SELECTION_METHOD)
			nuova_popolazione.append(self.crossover(parents[0], parents[1], CROSSOVER_METHOD))
			print(parents[0].name, "and", parents[1].name, "PRODUCED", nuova_popolazione[-1].name)

		# Applica la mutazione ai cromosomi nella nuova popolazione.
		for _ in range(MUTAZIONI):
			for chromosome in nuova_popolazione:
				self.mutation(chromosome, TASSO_MUTAZIONE / MUTAZIONI)
		print("__________________\n")

		# Verifica che la dimensione della nuova popolazione sia corretta e sostituisce la popolazione attuale con la nuova.
		assert len(nuova_popolazione) == len(self.Popolazione), "SURVIVORS_PER_GENERATION + NEWBORNS_PER_GENERATION != POPULATION_SIZE"
		self.Popolazione = nuova_popolazione

	def selection(self, num_selected, method):
		def roulette(population):
			total_fitness = sum(
				[c.avg_fitness() for c in population])  # Calcola la somma totale del fitness della popolazione.
			winner = randrange(
				int(total_fitness))  # Sceglie casualmente un valore vincitore all'interno della somma totale.
			fitness_so_far = 0

			# Itera attraverso la popolazione e seleziona il cromosoma il cui fitness cumulativo supera il valore vincitore.
			for chromosome in population:
				fitness_so_far += chromosome.avg_fitness()
				if fitness_so_far > winner:
					return chromosome

		if method == SelectionMethod.roulette:
			survivors = []
			# Itera per il numero specificato di cromosomi da selezionare.
			for _ in range(num_selected):
				# Usa la funzione roulette per selezionare un cromosoma dalla popolazione corrente.
				survivors.append(roulette([c for c in self.Popolazione if c not in survivors]))
			return survivors

		raise ValueError('SelectionMethod %s not implemented' % method)

	def crossover(self, c1, c2, method):
		def random_attributes():
			heuristics = {}
			# Per ogni funzione euristica, scegli casualmente da quale genitore prendere il valore.
			for fun, _ in c1.euristiche.items():
				heuristics[fun] = random.choice((c1, c2)).euristiche[fun]
			return Individuo(heuristics)

		def average_attributes():
			heuristics = {}
			# Per ogni funzione euristica, calcola la media dei valori dei genitori.
			for fun, _ in c1.euristica.items():
				heuristics[fun] = (c1.euristica[fun] + c2.euristica[fun]) / 2
			return Individuo(heuristics)

		if method == CrossoverMethod.random_attributes:
			return random_attributes()
		if method == CrossoverMethod.average_attributes:
			return average_attributes()
		raise ValueError('CrossoverMethod %s not implemented' % method)

	def mutation(self, individuo, mutation_rate):
		# Applica la mutazione con una certa probabilità per ciascuna funzione euristica del cromosoma.
		if randint(0, int(mutation_rate)) == 0:
			h = individuo.euristiche
			h[random.choice(list(h.keys()))] = randrange(-1000, 1000)
			print(individuo.name, "Mutato")

	def random_individuo(self):
		# Genera un cromosoma casuale con valori casuali per ogni funzione euristica.
		return Individuo({fun: randrange(-1000, 1000) for fun, weight in self.ai.euristiche.items()})

if __name__ == "__main__":
	GeneticAlgorithms().run()
