#!/usr/bin/python2.7
import cv2
import numpy as np
import sys

# Classifies board positions as White, Black, Empty

xl = 28
xr = 500-25
yt = 27
yb = 500-22


def main(argv):
    filename = argv[0]
    #game_board = cv2.imread("perspective-newgame.jpg", cv2.IMREAD_GRAYSCALE)
    game_board = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    board_classifier = BoardClassifier()
    game_squares = board_classifier.make_squares(game_board)
    classification = board_classifier.make_classification_matrix(game_board)
    for i in range(0,8):
        for j in range(0,8):
	    print classification[i][j],
        print

    numeric_classification_matrix = board_classifier.make_numeric_classification_matrix(classification)
    for i in range(0,8):
        for j in range(0,8):
	    print numeric_classification_matrix[i][j],
        print

    cv2.imshow("game board" , game_board)
    cv2.waitKey(0);

class BoardClassifier:
    def markup_board(self, board) :
        cv2.line(board, (0,0), (xl,yt), (0,255,0),5)
        cv2.line(board, (0,500), (xl,yb), (0,255,0),5)
        cv2.line(board, (500,0), (xr,yt), (0,255,0),5)
        cv2.line(board, (500,500), (xr,yb), (0,255,0),5)
        for i in range(0,9):
            x = int(xl + (i/8.0) * (xr - xl))
            cv2.line(board, (x, yt), (x, yb), (0,255,0), 3)
        for i in range(0,9):
            y = int(yt + (i/8.0) * (yb - yt))
            cv2.line(board, (xl, y), (xr, y), (0,255,0), 3)

    def make_squares(self, board) :
        squares = [[None for _ in range(8)] for _ in range(8)]
        for i in range(0,8):
            for j in range(0,8):
                square = self.get_square(board, i, j)
                squares[i][j] = square
        return squares
    
    
    def get_square(self, board, i, j):
        x = int(xl + (i/8.0) * (xr - xl))
        y = int(yt + (j/8.0) * (yb - yt))
        square = board [ y + 3 : -3 + y+(yb-yt)/8:1, x+3 : -3 + x+(xr - xl)/8:1 ]
        return square
    
    def compute_stdv(self, square) :
        return np.std(square)

    def compute_mean(self, square) :
        return np.mean(square)

    def color(self, i, j) :
        c = ((j % 2) + i) % 2
        if 0 == c:
            return "white"
        return "black"

    def classify(self, color, mean, stdv, square):
	mean_full = self.compute_mean(square)
        mean_middle = self.compute_mean(square[8:-8,8:-8])
        # print mean_full, mean_middle
        if stdv > 5:
            if color == "white" :
                if mean_middle > 148:
                    return "W"
                else:
                    return "B"
            else:
                if mean_middle > 80:
                    return "W"
                else:
                    return "B"
        else:
	    #return color + " unoccupied"
            return "X"

    def make_classification_matrix(self, board):
        classification = [[None for _ in range(8)] for _ in range(8)]
        squares = self.make_squares(board)
        for i in range(0,8) :
            for j in range(0,8) :
	        gs = squares[j][i]
                gsfloat = gs.astype(np.float)
	        stdv = self.compute_stdv(gsfloat[6:-6,6:-6])
                mean = self.compute_mean(gsfloat)
                color = self.color(i, j)
                classification[i][j] = self.classify(color, mean, stdv, gsfloat)
        return classification

    def make_numeric_classification_matrix(self, classification_matrix):
        numeric_classification_matrix = [[None for _ in range(8)] for _ in range(8)]
        for i in range(0,8) :
            for j in range(0,8) :
		if classification_matrix[i][j] == 'W':
                    numeric_classification_matrix[i][j] = 1;
                elif classification_matrix[i][j] == 'B':
                    numeric_classification_matrix[i][j] = -1;
                else:
                    numeric_classification_matrix[i][j] = 0;
        return np.array(numeric_classification_matrix, np.int8)
                    
    def compare_images_for_movement(rgbimage1, rgbimage2) :
        (rgbimage1b, rgbimage1g, rgbimage1r) = cv2.split(rgbimage1)
        val1 = np.mean(abs(rgbimage1r.astype(np.float)))
        (rgbimage2b, rgbimage2g, rgbimage2r) = cv2.split(rgbimage2)
        val2 = np.mean(abs(rgbimage2r.astype(np.float)))
        return (val2 - val1) > 2;

if __name__ == "__main__":
   main(sys.argv[1:])
