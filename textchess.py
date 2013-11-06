#!/opt/local/bin/python


import sys

chess = r'/Users/marc/devtools/bin/stockfish'.split()['linux' in sys.platform]

import subprocess as S
getprompt = 'isready'
done= 'readyok'

proc= S.Popen(chess, stdin=S.PIPE, stdout=S.PIPE, bufsize=1, universal_newlines=True)

print(proc.stdout.readline().strip())
proc.stdin.write('uci\n')

while True :
        text = proc.stdout.readline().strip()
        print(text)
        if text == "uciok":
            break
        
print('Choose skill level (0-20):')
skillLevel=str(raw_input())
proc.stdin.write('setoption name Skill Level value '+skillLevel+'\n')
proc.stdin.write('ucinewgame\n')

moveList='position startpos moves '
checkmate=False
while checkmate==False:
    print('Enter move:')
    move=str(raw_input())
    moveList=moveList+move+' '
    proc.stdin.write(moveList+'\n')
    #proc.stdin.write('go movetime 1000\n')
    proc.stdin.write('go nodes 100000\n')
    print('Computer moves:')
    while True :
        text = proc.stdout.readline().strip()
        if text[0:8] == 'bestmove':
            cpuMove=text[9:13]
            print(cpuMove)
            moveList=moveList+cpuMove+' '
            break
