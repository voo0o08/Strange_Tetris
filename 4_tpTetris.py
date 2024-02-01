# 처음에 오류 뜨면 콘솔이나 cmd창에서 "pip install 어쩌구" 어쩌구(= numpy, pygame..)해서 설치해주세요!!
import sys
import pygame
import numpy as np
import pandas as pd
from datetime import datetime as time
from random import randrange as rand

boxsize = 25                        # 칸 하나의 크기 지정
screenX = boxsize*30
screenY = boxsize*18
surface = pygame.display.set_mode((screenX, screenY))
WIDTH = 12                          # 양 테두리(2) + 가로 길이(10)
HEIGHT = 21                         # 하단 테두리(1) + 세로 길이(20)
boxsize = 20                        # 칸 하나의 크기 지정
field = np.zeros((HEIGHT, WIDTH))   # HEIGHT,WIDTH의 크기만큼 0으로 채움
field = field.tolist()              # data type을 list로 바꿈

pygame.init()
pygame.key.set_repeat(0,0)
pygame.display.set_caption(" TETRIS ")

time_set = set() # set(중복안됨) list(중복가능)
flow_time = 0 
score = 10000    # 원활한 아이템 사용을 위해 초기 점수를 10000점으로 설정했지만 기본값은 0임
line = 0
BLOCK = 0        # 플레이 필드 위에 뜨는 블록
N_BLOCK = 0      # 다음 블록 칸 위에 뜨는 블록
FPS = 10         # 새로고침 시간


# 블록 색 
COLORS = [
    (0,     0,   0), # 0 필드 검은색
    (0,   250,   0), # 1 블록 초록색
    (255, 255, 255), # 2 더미 흰색
    (127, 127, 127), # 3 벽  회색
    (255,   0,   0), # 4 무게 추
    (30,    0, 250)  # 5 블럭 하나짜리
    ]
 
# 블록 12종류 생성 (장재식)
pentomino_shapes = [
    [[0, 1, 1],
     [1, 1, 0],     # F
     [0, 1, 0]],
 
    [[0, 0, 0, 1],  # L
     [1, 1, 1, 1]],
 
    [[1, 1, 0, 0],  # N
      [0, 1, 1, 1]], 
 
    [[1, 0, 0],
     [1, 1, 1],     # T
     [1, 0, 0]],
 
    [[1, 0, 1],     # U
     [1, 1, 1]], 
 
    [[1, 1, 1, 1, 1]], # I
 
    [[1, 1, 0],     # P
     [1, 1, 1]],

    [[1, 0, 0],
     [1, 0, 0],     # V
     [1, 1, 1]],

    [[1, 0, 0],
     [1, 1, 0],     # W
     [0, 1, 1]],

    [[0, 1, 0],
     [1, 1, 1],     # X
     [0, 1, 0]],

    [[1, 1, 1, 1],  # Y
     [0, 1, 0, 0]],

    [[1, 1, 0],
     [0, 1, 0],     # Z
     [0, 1, 1]],
    
    [[4]], # 아이템(q) 추
    
    [[5]]  # 아이템(e) 한칸블럭
]

def stack():    # 하단을 벽돌로 바꿔주는 함수 (이윤서)
    global field, flow_time, time_set

    if (flow_time in time_set) == False: # 현재 시간이 time_set에 없으면 돌아감
        temp_line = []                   # 벽돌로 채울 공리스트를 생성
        for i in range(WIDTH):
            temp_line.append(3)          # 공리스트를 가로길이 만큼 3으로 채움
        field[-1-(len(time_set)+1)] = temp_line # 필드에서 가장 하단블록을 벽돌로 바꿈
    
    time_set.add(flow_time)              # 사용된 현재 시간은 time_set에 추가


def creatWall():    # field에 wall 생성 (이윤서)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if x == (WIDTH-1) or x == 0:
                field[y][x] = 3  # 필드 양끝을 벽돌 value 3으로 채움
            else:
                field[y][x] = 0
    for i in range(WIDTH):
        field[HEIGHT-1][i] = 3
    # (x = 0 or WIDTH-1)(y = HEIGHT-1)는 벽(3)으로, 그 외는 필드(0)
    
    
def drawField():    # 필드를 surface에 그림 (이윤서)
    global field 
    for y in range(HEIGHT):
        for x in range(WIDTH):
            value = field[y][x]
            pygame.draw.rect(surface, COLORS[value],(x*boxsize+boxsize, y*boxsize+boxsize, boxsize-3, boxsize-3),2) 


def moveField(direction, mWall):    # 필드 이동1 (이윤서)
    global field
    temp_field = pd.DataFrame(field)
    temp_field = temp_field.iloc[:,1:-1]                # 필드의 벽을 뺌
    move_col = temp_field.iloc[:,mWall]                 # 끝으로 이동할 한 열을 저장
    if direction == 'R':
        after_field = pd.concat([move_col,temp_field], axis=1, ignore_index=True) #순서 유의, 왼쪽에 붙음
        after_field = after_field.iloc[:,:-1]           # 맨 오른쪽 열을 자름
    elif direction == 'L':
        after_field = pd.concat([temp_field,move_col], axis=1, ignore_index=True) #순서 유의, 오른쪽에 붙음
        after_field = after_field.iloc[:,1:]            # 맨 왼쪽 열을 자름
    after_field.insert(loc=0,column='L_Wall',value=3)   # 맨 왼쪽에 벽 추가
    after_field.loc[:, 'R_Wall'] = 3                    # 벽 추가
    after_field = after_field.values.tolist()           # 리스트로 변환
    field = after_field                                 # 필드에 저장
    return field
    
    
def full_check():   # 블럭 칸 지우기 및 점수 증가 (이윤서)
    global field, score, line, time_set           
    sum_line = 0                            # 사라지는 줄의 수 체크
    blank_line = [3,0,0,0,0,0,0,0,0,0,0,3]  # 지운 칸에 넣어줄 빈 행
    for i in range(len(field)-1-len(time_set)):   
        if (0 in field[i]) == False:
            line += 1                       # 점수를 위한 줄 카운트
            sum_line += 1                   # 총 지운 줄 수를 카운트
            field.pop(i)                    # 필드에 0이 없다면 없앰
            field.insert(0, blank_line)     # 빈 행을 추가
            
    if sum_line == 1:                       # 지운 줄의 수가 1줄이라면 100점
        score += 100
    elif sum_line > 1:                      # 지운 줄의 수가 2줄 이상이라면 콤보로 1.5배
        score = int(score + sum_line*1.5*100)


def weight():   # 아이템(q) 추 (이윤서)
    global field
    for i in field:
        for j in i:
            if j == 4:                # 추(4)라면 해당 줄의 index를 저장
                weight_index = field.index(i)
                
    df_field = pd.DataFrame(field)    # 필드를 데이터 프레임으로 바꿈
    ary = np.array(field) 
    temp_field = ary[weight_index:,:] # 추 아래 전체 행을 저장 ----------------------1번
    temp_field = pd.DataFrame(temp_field)

    weight_col = temp_field.iloc[:,5] # 추가 있는 열을 저장
    weight_col = weight_col.tolist()  # 추가 있는 열을 리스트로 바꿈
    after_col = []                    # 아이템 사용 후 5번 열을 공리스트 생성
    for num in weight_col:            # 추가 있는 행의 아이템과 공백만 제거
      if num != 0 and num != 4:       
          after_col.append(num)       # 벽돌(1), 한칸 블록(5)이 아닐 경우 공리스트에 저장
    while len(after_col) != (len(field)-weight_index):
        after_col.insert(0, 0)        # 추가 있었던 행의 남은 윗칸은 0으로 채워 크기를 맞춤
    after_col = pd.DataFrame(after_col) 
    temp_field.iloc[:,5] = after_col  # 1번 프레임에서 5번 열을 추와 공백을 없앤 열로 바꿈--2번
    df_field.iloc[weight_index:,:] = temp_field # 전체 필드에 1번 프레임을 2번 프레임으로 바꿈
    field = df_field.values.tolist()  # 리스트로 교체 후 필드에 저장

    
def rotate_counterclockwise(shape): # 블록 회전1 (장재식)(*참고)
    return [
        [ shape[y][x] for y in range(len(shape)) ]
        for x in range(len(shape[0]) - 1, -1, -1)
    ]

    
def collision(field, shape, xpos, ypos, plus): # 블록 충돌 (이경진)(*참고)
    xoff, yoff = plus
    for by, row in enumerate(shape): # Block.creatBlock() 참고
        for bx, box in enumerate(row):
            try:
                if box and field[ by+ypos +yoff ][ bx+xpos +xoff-1 ]: 
                    return True      # box & field[y][x] 모두 True(0이 아님)가 되면 실행
            except IndexError:
                return True
    return False                     # 블록에 대한 충돌 검사가 끝나면 리턴


def pasteBlock(shape, xpos, ypos, plus, num):    # 필드에 멈춘 블록 저장 (이경진)(*참고)
    global field
    xoff, yoff = plus
    for by, row in enumerate(shape):
        for bx, val in enumerate(row):
            if val == 0 or val == 4 or val == 5: # 벽(0)과 추(5), 한칸블록이면 그대로
                field[ by+ypos +yoff ][ bx+xpos +xoff ] += val
            else:                                # 그 외라면 더미(2)로 저장
                field[ by+ypos +yoff ][ bx+xpos +xoff ] += 2

    if num == 4:                                 # 추(4)라면 추 알고리즘으로 넘어감
        weight()
        
        
def get():  # 블록 클래스를 생성 (이윤서)
     Block_num = rand(len(pentomino_shapes)-2)
                              # 모양의 -2까지는 아이템이기에 제외한 나머지 중 랜덤으로 뽑음
     block = Block(Block_num) # 클래스 생성
     return block             # 클래스 리턴

class Block:
    def __init__(self, Block_num):
        self.shape = pentomino_shapes[Block_num]
        self.xpos = int(WIDTH/2 - len(self.shape[0])/2 + 1 ) # 중앙배치
        self.ypos = 1 # 상단배치
        self.field = field
        self.gameover = False
        self.num = 0 
        if collision(self.field, self.shape, self.xpos, self.ypos, (0,0)):
            self.gameover = True
            
    def drawBlock(self):  # 블록을 필드에 그림 (이경진)(*참고)
        if not self.gameover:
            for y, row in enumerate(self.shape): # shape를 행(row)별로 찢음
                for x, val in enumerate(row):    # shape의 행(row)을 하나씩 찢음
                    if val:
                        pygame.draw.rect(surface,
                                         COLORS[val],
                                         ( (self.xpos+x)*boxsize, (self.ypos+y)*boxsize, boxsize-3, boxsize-3 ),2) 
                        if val == 4:             # 블록 값이 추(4)면 self.num도 4로 바꿈
                            self.num = 4
                        
    def draw_next(self):  # 다음 블록 미리보기 (이윤서)
        for y, row in enumerate(self.shape):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(surface,
                                     COLORS[val],
                                     ((self.xpos+x)*(boxsize-2)+260, (self.ypos+y)*(boxsize-2)+50, boxsize-5, boxsize-5 ), 2) 
        
    def moveD(self, direction, plus):  # 필드 이동2 (이경진)
        if not collision(self.field, self.shape, self.xpos, self.ypos, plus):
            if direction == 'R':       # 방향이 오른쪽일 때
                self.field = moveField(direction, -1)
            elif direction == 'L':     # 방향이 왼쪽일 때
                self.field = moveField(direction, 0)


    def down(self, direction, plus): # 블록을 아래로 이동 (이경진)
        global BLOCK, N_BLOCK
        self.field = field
        if self.gameover == False:
            if collision(self.field, self.shape, self.xpos, self.ypos, plus):
                pasteBlock(self.shape, self.xpos, self.ypos, (-1,-1), self.num) 
                BLOCK = N_BLOCK
                N_BLOCK = get()
                self.gameover = True
            else: # 충돌에서 걸리지 않는다면 아래로 한 칸 이동
                self.ypos += 1
        full_check()


    def space(self, plus):  # 수직 낙하 (이경진)
        global BLOCK, N_BLOCK, score
        self.field = field
        score += 10 # 수직 낙하를 할 때마다 10점 추가
        while self.gameover == False: # 게임오버가 될 때까지 반복
            if collision(self.field, self.shape, self.xpos, self.ypos, plus):
                pasteBlock(self.shape, self.xpos, self.ypos, (-1,-1), self.num)   
                BLOCK = N_BLOCK
                N_BLOCK = get()
                self.gameover = True
            else:   # 충돌에서 걸리지 않는다면 아래로 한 칸 이동
                self.ypos += 1
        full_check()
        
        
    def rotate_shape(self): # 블록 회전2 (장재식)
        if not self.gameover:
            new_shape = rotate_counterclockwise(self.shape)
            if not collision(self.field, new_shape, self.xpos, self.ypos, (0,0)):
                self.shape = new_shape
    
    def gameoverC(self): # 게임오버 상태 리턴
        if self.gameover:
            return True
 

def checkForKeyPress(): # 키보드가 눌리고 안 눌린 상태를 확인 (이경진)(*참고)
   for event in pygame.event.get([pygame.KEYDOWN,pygame.KEYUP]):
       if event.type == pygame.KEYDOWN:
           continue
       return event.key
   return None 


def makeMSG(text,size,color,pos): # surface에 나타낼 문자의 형식 지정1 (이경진)
    font = pygame.font.Font("DungGeunMo.ttf", size)
    msgBox = font.render(text,True,color)
    surface.blit(msgBox, pos)

def makeMSGd(text,size,color,pos, D): 
    # surface에 나타낼 문자의 형식 지정2 (특수문자(u)/중앙정렬(c)/우측정렬(r)) (이경진)
    xpos, ypos = pos
    if D == 'u':
        font = pygame.font.Font("NanumSquareB.ttf", size)
    else:
        font = pygame.font.Font("DungGeunMo.ttf", size)
    msgBox = font.render(text,True,color)
    msgRect = msgBox.get_rect()
    if D == 'c':
        msgRect.center = (int(screenX/2)+xpos, int(screenY/2)+ypos)
    elif D == 'u':
        msgRect.center = ((boxsize*xpos+3, boxsize*ypos))
    elif D == 'r':
        msgRect.midright = ((boxsize*xpos, boxsize*ypos))
    surface.blit(msgBox,msgRect)

    
def startScreen(): # 시작 화면 (이경진)
    global CLK
    surface.fill((0,0,0))
    makeMSGd('TETRIS', 100, (200,200,200), (5,-20), 'c')
    makeMSGd('TETRIS', 100, (0,250,0), (0,-25), 'c')
    makeMSGd('키보드를 누르면 게임이 실행됩니다.', 15, (255,255,255), (0,30), 'c')
    
    while checkForKeyPress() == None: # 키보드 인식이 될 때까지 반복
        pygame.display.update()
        CLK.tick()

def gameScreen1(): # 진행 화면1 - 변화 (이경진)
    global score, line
    pygame.draw.rect( surface, COLORS[0], (14*boxsize, 2*boxsize, 180, 250) ) 
    
    makeMSG('NEXT BLOCK', 17, (255,255,255), (boxsize*14+10, boxsize*2))
    
    makeMSG('TIME',17, (255,255,255), (boxsize*14+10,boxsize*7))
    makeMSGd(str(flow_time), 20, (255,255,255), (21,8), 'r')
    
    makeMSG('LINE', 17, (255,255,255), (boxsize*14+10,boxsize*9))
    makeMSGd(str(line), 20, (255,255,255), (21,10), 'r')
    
    makeMSG('SCORE', 17, (255,255,255), (boxsize*14+10,boxsize*11))
    makeMSGd(str(score), 20, (255,255,255), (21,12), 'r')

def gameScreen2(): # 진행 화면2 - 고정 (이경진)
    makeMSG('ESC   : 게임 종료', 17, (255,255,255), (boxsize*25, boxsize*2))
    makeMSG('SPACE : 수직 낙하', 17, (255,255,255), (boxsize*25, boxsize*3))
    makeMSG('P     : 일시 정지', 17, (255,255,255), (boxsize*25, boxsize*4)) 
    
    makeMSG('ITEM    (사용시 점수 차감)', 17, (255,255,255), (boxsize*25, boxsize*7))
    makeMSG('Q     : 무게  추  (-500)', 17, (255,255,255), (boxsize*25, boxsize*8))
    makeMSG('W     : 블록 패스 (-300)', 17, (255,255,255), (boxsize*25, boxsize*9))
    makeMSG('E     : 한칸 블록 (-100)', 17, (255,255,255), (boxsize*25, boxsize*10)) 
    
    makeMSGd('▲', 18, (255,255,255), (26, 13), 'u')
    makeMSG('      : 회전', 17, (255,255,255), (boxsize*25, boxsize*12+10))
    makeMSGd('◀     ▶', 18, (255,255,255), (26, 14), 'u')
    makeMSG('      : 좌 / 우 ', 17, (255,255,255), (boxsize*25, boxsize*13+10))
    makeMSGd('▼', 18, (255,255,255), (26, 15), 'u')
    makeMSG('      : 아래', 17, (255,255,255), (boxsize*25, boxsize*14+10))

def pauseScreen(): # 정지 화면 (이경진)
    surface.fill((0,0,0))
    makeMSGd('PAUSE', 100, (200,200,200), (5,-120), 'c')
    makeMSGd('PAUSE', 100, (0,250,0), (0,-125), 'c')
    makeMSGd('P를 누르면 게임이 재개됩니다.', 15, (255,255,255), (0,-70), 'c')
    
    makeMSGd('ESC   : 게임 종료', 16, (255,255,255), (0,0), 'c')
    makeMSGd('SPACE : 수직 낙하', 16, (255,255,255), (0,boxsize), 'c')
    makeMSGd('P     : 일시 정지', 16, (255,255,255), (0,boxsize*2), 'c')
    
    makeMSGd('ITEM    (사용시 점수 차감)', 16, (255,255,255), (0,boxsize*4), 'c')
    makeMSGd('Q : 무게  추  (-500)', 16, (255,255,255), (0,boxsize*5), 'c')
    makeMSGd('W : 블록 패스 (-300)', 16, (255,255,255), (0,boxsize*6), 'c')
    makeMSGd('E : 한칸 블록 (-100)', 16, (255,255,255), (0,boxsize*7), 'c')

    
def gameQuit(): # 종료 화면 (이경진)
    print("GAMEOVER!!")
    surface.fill((0,0,0))
    makeMSGd('GAME OVER', 100, (200,200,200), (5,-80), 'c')
    makeMSGd('GAME OVER', 100, (0,250,0), (0,-85), 'c')
    makeMSGd('키보드를 누르면 게임이 종료됩니다.', 15, (255,255,255), (0,-30), 'c')
    writeFile()
    
    while checkForKeyPress() == None: # 키보드 인식이 될 때까지 반복
        pygame.display.update()
        CLK.tick()
        
def writeFile():    # 점수 정리 (이경진)
    global score
    score_list = []
    filename = "score.txt"
    
    f = open(filename, 'a')         # 파일을 추가 모드로 엶, 만약 파일이 없다면 생성
    f.write(str(score)+"\n")        # 현재 점수를 파일에 추가
    f.close()

    f = open(filename, 'r')         # 파일을 읽기 모드로 엶
    lines = f.readlines()           # 파일을 줄별로 읽어 리스트 형식으로 저장
    for line in lines:
        score_list.append(int(line.strip()))
        # 각 줄의 줄바꿈 문자를 제거(line.strip())하여 스코어 리스트에 넣음 (정수형으로 넣어야 내림차순 정렬 가능)
    f.close()
    
    score_list.sort(reverse=True)   # 점수리스트 내림차순 정렬

    if len(score_list) < 5:         # 실행 횟수가 5 미만이면 모든 점수 순위별 출력
        for i in range(len(score_list)): 
            text = "{0}위   {1}점".format(str(i+1), str(score_list[i]))
            makeMSGd(text, 16, (255,255,255), (0,boxsize*(2+i)), 'c')
    else:                           # 실행 횟수가 5 이상이면 점수별 상위 5등까지 나타냄
        for i in range(5):
            text = "{0}위   {1}점".format(str(i+1), str(score_list[i]))
            makeMSGd(text, 16, (255,255,255), (0,boxsize*(2+i)), 'c')

    rank = score_list.index(score)+1 # 현재 점수의 순위
    ranktext = "{0}위   {1}점".format(str(rank), str(score))
    makeMSGd(ranktext, 16, (0,250,0), (0,boxsize*8), 'c')

########################################################################################################

def main():
    global BLOCK, N_BLOCK, score, flow_time, CLK
    if BLOCK == 0: BLOCK = get()    # main문에 클래스 생성, get의 리턴값이 클래스라서 BLOCK 또한 클래스
    if N_BLOCK == 0: N_BLOCK = get()# 클래스 생성
    key = None                  # 초기 설정
    gamePause = keyUP = keyDOWN = keyLEFT = keyRIGHT = False # 초기 설정
    pause_start = pause_sum = 0 # 초기 설정
    CLK = pygame.time.Clock()
    startScreen() # 시작 화면 실행
    start_time = time.now()
    pygame.time.set_timer(pygame.USEREVENT, 1500) # 1.5초(1500ms)마다 이벤트 반복
    surface.fill((0,0,0))
    creatWall()
    gameScreen2()
    while True:
        if gamePause: # gamePause == True 
            pauseScreen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:          # 종료키 종료
                    gameQuit()
                    pygame.quit() 
                    sys.exit() 
                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_p: # 일시정지(p)를 다시 누르면 실행
                        gamePause = False
                        surface.fill((0,0,0))
                        pause_stop = time.now()
                        pause = (pause_start - pause_stop).seconds - 86400
                                                # 일시정지 시켜놓은 시간만큼 측정
                        pause_sum += pause      # 위를 저장
                        gameScreen2()
                    elif event.key == pygame.K_ESCAPE: # esc 종료
                        gameQuit()
                        pygame.quit() 
                        sys.exit() 
                        
        else: # gamePause == False
            now_time = time.now() 
            flow_time = (-(start_time - now_time)).seconds +pause_sum
            drawField()
            gameScreen1()
            BLOCK.drawBlock()
            N_BLOCK.draw_next()
            
            for event in pygame.event.get(): # 이벤트 인식
                if event.type == pygame.USEREVENT: BLOCK.down('D', (0,0))
                if event.type == pygame.QUIT or BLOCK.gameover == True:
                    gameQuit()                   # 종료키 종료와 게임오버 판단
                    pygame.quit() 
                    sys.exit() 
                if event.type == pygame.KEYDOWN: # 키보드를 누를 때 반응
                    key = event.key              # event.key 활성화
                    if key == pygame.K_UP: keyUP = True
                    elif key == pygame.K_RIGHT: keyRIGHT = True
                    elif key == pygame.K_LEFT: keyLEFT = True
                    elif key == pygame.K_DOWN: keyDOWN = True
                    elif key == pygame.K_SPACE : BLOCK.space((0,0))
                    elif key == pygame.K_ESCAPE: # esc 종료
                        gameQuit() 
                        pygame.quit() 
                        sys.exit() 
                    elif key == pygame.K_p: 
                        pause_start = time.now()
                        gamePause = True
                elif event.type == pygame.KEYUP: # 키보드를 뗄 때 반응
                    key = None                   # event.key 비활성화
                    if event.key == pygame.K_UP: keyUP = False
                    elif event.key == pygame.K_RIGHT: keyRIGHT = False
                    elif event.key == pygame.K_LEFT: keyLEFT = False
                    elif event.key == pygame.K_DOWN: keyDOWN = False
    
            if keyUP == True: BLOCK.rotate_shape()
            elif keyRIGHT == True: BLOCK.moveD('R', (-1,-1))
            elif keyLEFT == True: BLOCK.moveD('L', (1,-1))
            elif keyDOWN == True: BLOCK.down('D', (0,0))
             
            if score >= 500 and key == pygame.K_q:   # 아이템 추(q)
                score -= 500        # 점수 500점 차감
                N_BLOCK = Block(12) # 다음 블록 추(4) 지정
            elif score >= 300 and key == pygame.K_w: # 아이템 블록패스(w)
                score -= 300        # 점수 300점 차감
                BLOCK = N_BLOCK 
                N_BLOCK = get()
            elif score >= 100 and key == pygame.K_e: # 아이템 한칸블록(e)
                score -= 100        # 점수 100점 차감
                N_BLOCK = Block(13) # 다음 블록 한칸블록(5) 지정
                
            if (flow_time % 100 == 0 and flow_time != 0):  
                stack()

        pygame.display.update()
        CLK.tick(FPS)
        
if __name__ == '__main__':
    main()
        
