
def _is_block(cell):
	return cell != 0

def _is_empty(cell):
	return cell == 0

def _holes_in_board(board):
	"""Un buco è definito come uno spazio vuoto sotto un blocco. Il blocco non
	deve essere direttamente sopra la buca per essere conteggiato. Questa funzione
	 identifica qualsiasi buca e le restituisce sotto forma di una lista di tuple (x, y)
	"""
	holes = []
	block_in_col = False
	for x in range(len(board[0])):
		for y in range(len(board)):
			if block_in_col and _is_empty(board[y][x]):
				holes.append((x,y))
			elif _is_block(board[y][x]):
				block_in_col = True
		block_in_col = False
	return holes

def num_holes(board):
	"""numero di buchi """
	return len(_holes_in_board(board))

def num_blocks_above_holes(board):
	"""numero di  blocchi presenti sopra un buco"""
	c = 0
	for hole_x, hole_y in _holes_in_board(board):
		for y in range(hole_y-1, 0, -1):
			if _is_block(board[y][hole_x]):
				c += 1
			else:
				break
	return c

def num_gaps(board):

	gaps = []
	sequence = 0
	board_copy = []


	for y in range(len(board)):
		board_copy.append([1] + board[y] + [1])

	for y in range(len(board_copy)):
		for x in range(len(board_copy[0])):
			if sequence == 0 and _is_block(board_copy[y][x]):
				sequence = 1
			elif sequence == 1 and _is_empty(board_copy[y][x]):
				sequence = 2
			elif sequence == 2:
				if _is_block(board_copy[y][x]):
					gaps.append(board_copy[y][x-1])
					sequence = 1
				else:
					sequence = 0

	return len(gaps)	

def max_height(board):

	for idx, row in enumerate(board):
		for cell in row:
			if _is_block(cell):
				return len(board) - idx-1

def avg_height(board):

	total_height = 0
	for height, row in enumerate(reversed(board[1:])):
		for cell in row:
			if _is_block(cell):
				total_height += height
	return total_height / num_blocks(board)

def num_blocks(board):

	c = 0
	for row in board:
		for cell in row:
			if _is_block(cell):
				c += 1
	return c