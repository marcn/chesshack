#/usr/bin/env python

from ChessBoard import ChessBoard

import os, pygame,math
from pygame.locals import *

from pprint import pprint

class ChessClient:

    def mainLoop(self):    
        pygame.init()    
        
        pieces = {}    
        chess = ChessBoard()
        board = chess.getBoard()
        turn = chess.getTurn()

        screen = pygame.display.set_mode((480, 480),1)
        pygame.display.set_caption('ChessBoard Client')

        # load all images
        pieces = [{},{}]
        pieces[0]["r"] = pygame.image.load("./img.sample/brw.png")                
        pieces[0]["n"] = pygame.image.load("./img.sample/bnw.png")                
        pieces[0]["b"] = pygame.image.load("./img.sample/bbw.png")                
        pieces[0]["k"] = pygame.image.load("./img.sample/bkw.png")                
        pieces[0]["q"] = pygame.image.load("./img.sample/bqw.png")                
        pieces[0]["p"] = pygame.image.load("./img.sample/bpw.png")                
        pieces[0]["R"] = pygame.image.load("./img.sample/wrw.png")                
        pieces[0]["N"] = pygame.image.load("./img.sample/wnw.png")                
        pieces[0]["B"] = pygame.image.load("./img.sample/wbw.png")                
        pieces[0]["K"] = pygame.image.load("./img.sample/wkw.png")                
        pieces[0]["Q"] = pygame.image.load("./img.sample/wqw.png")                
        pieces[0]["P"] = pygame.image.load("./img.sample/wpw.png")                
        pieces[0]["."] = pygame.image.load("./img.sample/w.png")                
        pieces[1]["r"] = pygame.image.load("./img.sample/brb.png")                
        pieces[1]["n"] = pygame.image.load("./img.sample/bnb.png")                
        pieces[1]["b"] = pygame.image.load("./img.sample/bbb.png")                
        pieces[1]["k"] = pygame.image.load("./img.sample/bkb.png")                
        pieces[1]["q"] = pygame.image.load("./img.sample/bqb.png")                
        pieces[1]["p"] = pygame.image.load("./img.sample/bpb.png")                
        pieces[1]["R"] = pygame.image.load("./img.sample/wrb.png")                
        pieces[1]["N"] = pygame.image.load("./img.sample/wnb.png")                
        pieces[1]["B"] = pygame.image.load("./img.sample/wbb.png")                
        pieces[1]["K"] = pygame.image.load("./img.sample/wkb.png")                
        pieces[1]["Q"] = pygame.image.load("./img.sample/wqb.png")                
        pieces[1]["P"] = pygame.image.load("./img.sample/wpb.png")                
        pieces[1]["."] = pygame.image.load("./img.sample/b.png")                

        clock = pygame.time.Clock()

        posRect = pygame.Rect(0,0,60,60)

        mousePos = [-1,-1]
        markPos = [-1,-1]
        validMoves = []
        
        gameResults = ["","WHITE WINS!","BLACK WINS!","STALEMATE","DRAW BY THE FIFTHY MOVES RULE","DRAW BY THE THREE REPETITION RULE"]
        
        while 1:
            clock.tick(30)        
    
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                    elif event.key == K_LEFT:
                        chess.undo()
                    elif event.key == K_RIGHT:
                        chess.redo()
                    elif event.unicode in ("f","F"):
                        print chess.getFEN()
                    elif event.unicode in ("a","A"):
                        an = chess.getAllTextMoves(chess.AN)
                        if an:
                            print "AN: " + ", ".join(an)
                    elif event.unicode in ("s","S"):
                        san = chess.getAllTextMoves(chess.SAN)
                        if san:
                            print "SAN: " + ", ".join(san)
                    elif event.unicode in ("l","L"):
                        lan = chess.getAllTextMoves(chess.LAN)
                        if lan:
                            print "LAN: " + ", ".join(lan)
                    board = chess.getBoard()
                    turn = chess.getTurn()
                    markPos[0] = -1
                    validMoves = [] 
                        
                if not chess.isGameOver():
                    if event.type == MOUSEMOTION:
                        mx = event.pos[0]
                        my = event.pos[1]
                        mousePos[0] = mx/60
                        mousePos[1] = my/60
                    elif event.type == MOUSEBUTTONDOWN:
                        if mousePos[0] != -1:
                            if markPos[0] == mousePos[0] and markPos[1] == mousePos[1]:
                                markPos[0] = -1
                                validMoves = []
                            else: 
                                if (turn==ChessBoard.WHITE and board[mousePos[1]][mousePos[0]].isupper()) or \
                                   (turn==ChessBoard.BLACK and board[mousePos[1]][mousePos[0]].islower()):    
                                    markPos[0] = mousePos[0]
                                    markPos[1] = mousePos[1]
                                    validMoves = chess.getValidMoves(tuple(markPos))
                                    
                                else:
                                    if markPos[0] != -1:
                                        res = chess.addMove(markPos,mousePos)
                                        if not res and chess.getReason() == chess.MUST_SET_PROMOTION:
                                            chess.setPromotion(chess.QUEEN)                                                
                                            res = chess.addMove(markPos,mousePos)                                            
                                        if res:
                                            #print chess.getLastMove()
                                            print chess.getLastTextMove(chess.SAN)
                                            board = chess.getBoard()
                                            turn = chess.getTurn()
                                            markPos[0] = -1
                                            validMoves = [] 

            if chess.isGameOver():
                pygame.display.set_caption("Game Over! (Reason:%s)" % gameResults[chess.getGameResult()])
                validMove = []
                markPos[0] = -1
                markPos[1] = -1
            else:
                pygame.display.set_caption('ChessBoard Client') 
                                            
            y = 0
            for rank in board:
                x = 0
                for p in rank:
                    screen.blit(pieces[(x+y)%2][p],(x*60,y*60))
                    x+=1
                y+=1             

            if markPos[0] != -1:
                posRect.left = markPos[0]*60
                posRect.top = markPos[1]*60
                pygame.draw.rect(screen, (255,255,0),posRect, 4)

            for v in validMoves:
                posRect.left = v[0]*60
                posRect.top = v[1]*60
                pygame.draw.rect(screen, (255,255,0),posRect, 4)
                                       
            pygame.display.flip()        

def main():
    g = ChessClient()
    g.mainLoop()

 
#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()


