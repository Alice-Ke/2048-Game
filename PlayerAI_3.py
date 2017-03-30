from random import randint
from BaseAI import BaseAI
# from GridU_3       import GridU
from Grid_3 import Grid
from ComputerAI_3 import ComputerAI
from Displayer_3  import Displayer
from random       import randint
import time
from math import log2
from math import inf
from math import log



class PlayerAI(BaseAI):

	# no use
	def ifCorner( self, grid ):
		sumV = 0
		l = grid.size
		m = grid.getMaxTile()
		# row
		for j in [ 0, l - 1]:
			for i in range( l ):
				# row
				if m == grid.getCellValue( [ j, i ]):
					sumV = sumV + 1
				# column
				if m == grid.getCellValue( [ i, j ]):
					sumV = sumV + 1
		return sumV

	def smooth( self, grid ):
		l = grid.size
		smooth = 0
		for x in range( l ) :
			for y in range( l ):
				nowV = grid.getCellValue( [x, y] ) 
				if nowV != 0:
					# left -> right scan farest value
					j = y
					while True:
						j = j + 1
						neighborV = grid.getCellValue( [ x, j ] )
						if neighborV != 0:
							break
					if neighborV != None:
						smooth = smooth - abs( log2( neighborV )  - log2( nowV ) )
					
					# up -> down scan farest value
					i = x
					while True:
						i = i + 1
						neighborV = grid.getCellValue( [ i, y ] )
						if neighborV != 0:
							break
					if neighborV != None:
						smooth = smooth - abs( log2( neighborV ) -  log2( nowV )  )
		return smooth

	def mono( self, grid ):
		l = grid.size
		count = [ 0 ] * 4 
		# column direction 
		for y in range( l ):
			now = 0;
			next = now + 1;
			while( next < l ):
				while( next < l and not grid.getCellValue( [ next, y ] ) ):
					next = next + 1
				if next >= l:
					next = next - 1
				nowTemp = grid.getCellValue( [ now, y ] )
				nowV = log2( nowTemp )if nowTemp != 0 else 0 
				nextTemp = grid.getCellValue( [ next, y ] )
				nextV = log2( nextTemp )if nextTemp != 0 else 0 
				if nowV > nextV:
					count[ 0 ] = count[ 0 ] + nextV - nowV
				else:
					count[ 1 ] = count[ 1 ] + nowV - nextV
				now = now + 1
				next = next + 1
		#left or right 
		for x in range( l ):
			now = 0
			next = now + 1 
			while( next < l ):
				while( next < l and not grid.getCellValue( [ x, next ] ) ):
					next = next + 1
				if next >= l:
					next = next - 1
				nowTemp = grid.getCellValue( [ x, now ] )
				nowV = log2( nowTemp )if nowTemp != 0 else 0
				nextTemp = grid.getCellValue( [ x, next ] )
				nextV = nextTemp if nextTemp != 0 else 0
				if nowV > nextV:
					count[ 2 ] = count[ 2 ] + nextV - nowV
				else:
					count[ 3 ] = count[ 3 ] + nowV - nextV
				now = now + 1
				next = next + 1 
		# give the final value 
		countT = max( count[ 0 ], count[ 1 ] ) + max( count[ 2 ], count[ 3 ] )
		return countT

	# this is the version with alpha-beta pruning
	def getMove( self, grid ):
		( move, child, utility ) = self.maximize( 3, grid, -inf, inf )
		return move

	# return ( maxMove, maxChild, maxUtility )
	def maximize( self, depth, state, alpha, beta ):
		if depth <= 0 or not state.canMove():
			return ( None, None, self.hf( state ) )

		( maxMove, maxChild, maxUtility ) = ( -1, None, -inf )
		# if copy necessary?
		for move in state.getAvailableMoves():
			child = state.clone()
			child.move( move )

			( temp1, temp2, utility ) = self.minimize( depth - 1, child, alpha, beta )
			if utility > maxUtility:
				( maxMove, maxChild, maxUtility ) = ( move, child, utility )
			# do alpha-beta prunning
			if maxUtility >= beta:
				break 
			if maxUtility > alpha:
				alpha = maxUtility
		return ( maxMove, maxChild, maxUtility )

	# return ( minPos, minChild, minUtility )
	def minimize( self, depth, state, alpha, beta ):
		if depth <= 0:
			return ( None, None, self.hf( state) )
		( minPos, minChild, minUtility ) = ( None, None, inf )
		for pos in state.getAvailableCells():
			for i in [ 2, 4 ]:
				child = state.clone()
				child.insertTile( pos , i )
				# child.previousPos = pos
				( temp1, temp2, utility ) = self.maximize( depth - 1, child, alpha, beta )
				if utility < minUtility:
					( minPos, minChild, minUtility ) = ( pos, child, utility)
				if minUtility <= alpha:
					break
				if minUtility < beta:
					beta = minUtility
		return ( minPos, minChild, minUtility )

	# this is the version for pure minimax
	# def getMove( self, grid ):
	#     ( move, child, utility ) = self.maximize( 3, grid )
	#     return move

	# # return ( maxMove, maxChild, maxUtility )
	# def maximize( self, depth, state ):
	#     if depth <= 0 or not state.canMove():
	#         return ( None, None, self.hf( state ) )

	#     ( maxMove, maxChild, maxUtility ) = ( -1, None, -inf )
	#     # if copy necessary?
	#     for move in state.getAvailableMoves():
	#         child = state.clone()
	#         child.move( move )

	#         ( temp1, temp2, utility ) = self.minimize( depth - 1, child )
	#         if utility > maxUtility:
	#             ( maxMove, maxChild, maxUtility ) = ( move, child, utility )
	
	#     return ( maxMove, maxChild, maxUtility )

	# # return ( minPos, minChild, minUtility )
	# def minimize( self, depth, state ):
	#     if depth <= 0:
	#         return ( None, None, self.hf( state) )
	#     ( minPos, minChild, minUtility ) = ( None, None, inf )
	#     for pos in state.getAvailableCells():
	#         for i in [ 2, 4 ]:
	#             child = state.clone()
	#             child.insertTile( pos , i )
	#             # child.previousPos = pos
	#             ( temp1, temp2, utility ) = self.maximize( depth - 1, child )
	#             if utility < minUtility:
	#                 ( minPos, minChild, minUtility ) = ( pos, child, utility)
	#     return ( minPos, minChild, minUtility )

	def hf( self, state ):
		monotonicity = self.mono( state )
		spaceNum = len( state.getAvailableCells( ) )
		# spaceTemp = log( spaceNum ) if spaceNum != 0 else 0
		maxValue = log2( state.getMaxTile() )
		smoothness = self.smooth( state )
		corner = self.ifCorner( state )
		# print( spaceNum, monotonicity, maxValue, smoothness, corner  )
		return spaceNum * 2.7 + monotonicity * 1.0 + maxValue * 0.8 + smoothness * 0.1
		
	
# a one step try
# def main():
#     g = Grid()
#     g.map[0][0] = 2
#     g.map[1][0] = 2
#     g.map[3][0] = 4

#     p = PlayerAI()
#     print( p.getMove( g ) )

# if __name__ == '__main__':
#     main()
		




