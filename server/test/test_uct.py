import unittest
import sys
import math

sys.path.append("../")

from uct import OXOState
from uct import OXOStateEX

class TestOXOState(unittest.TestCase):  

    def test_OXOState_1(self):
        state = OXOState()
        print("OXOState -- GetMoves: " + str(state.GetMoves()))
        self.assertEqual(len(state.GetMoves()), 9) 

class TestOXOStateEX(unittest.TestCase):  

    def test_OXOStateEx_1(self):
        board_size = 11
        win_length = 5
        state = OXOStateEX(board_size, win_length)
        self.assertEqual(len(state.GetMoves()), math.pow(board_size,2)) 
    
    def test_OXOStateEx_GetResult_1(self):
        board_size = 3
        win_length = 3
        state = OXOStateEX(board_size, win_length)

        state.board = [0,0,0,1,1,1,0,0,0]
        self.assertEqual(state.IsHorizontalSame(0,1,1), True)
        #print("OXOStateEx_GetResult: " + str(state.board))
        self.assertEqual(state.GetResult(1), 1.0) 

        state.board = [1,0,0,1,0,0,1,0,0]
        self.assertEqual(state.IsVerticalSame(0,0,1), True)
        #print("OXOStateEx_GetResult: " + str(state.board))
        self.assertEqual(state.GetResult(1), 1.0) 


        state.board = [1,0,0,0,1,0,0,0,1]
        self.assertEqual(state.IsInclinedSame(0,0,1), True)
        #print("OXOStateEx_GetResult: " + str(state.board))
        self.assertEqual(state.GetResult(1), 1.0) 

        state.board = [0,0,1,0,1,0,1,0,0]
        self.assertEqual(state.IsInclinedSame(2,0,1), True)
        #print("OXOStateEx_GetResult: " + str(state.board))
        self.assertEqual(state.GetResult(1), 1.0) 

    def test_OXOStateEx_DoMove_1(self):
        board_size = 3
        win_length = 3
        state = OXOStateEX(board_size, win_length)

        for i in range(board_size*board_size):
            state.DoMove(i)
        
        steps = [x for x in range(board_size*board_size)]

        #print("OXOStateEx_DoMove:" + str(state.steps))

        self.assertListEqual(state.steps, steps)

            


if __name__ == '__main__':
    unittest.main()