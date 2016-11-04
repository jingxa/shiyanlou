'''
状态机:
    Init: init()
        Game
    Game: game()
        Game
        Win
        GameOver
        Exit
    Win: lambda: not_game('Win')
        Init
        Exit
    Gameover: lambda: not_game('Gameover')
        Init
        Exit
    Exit: 退出循环
'''


import curses
from random import randrange,choice
from collections import defaultdict

#定义输入行为 W（上），A（左），S（下），D（右），R（重置），Q（退出）
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
#有效键值列表
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
#输入与行为进行关联
actions_dict = dict(zip(letter_codes,actions*2))
#print(action_dict)

#游戏操作类
class GameField():
    def __init__(self,height=4,width=4,win=2048):
        self.height = height    #高
        self.width = width      #宽
        self.win_value = 2048   #过关分数
        self.score = 0          #当前得分
        self.highscore = 0      #最高得分
        self.reset()            #棋盘重置


    def spawn(self):
        new_element = 4 if randrange(100) > 89 else 2
        (i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def reset(self):
        '''
        重置棋盘
        :return:
        '''
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        #生成两个初始值
        self.spawn()
        self.spawn()


    #游戏移动操作
    def move(self,direction):
        '''
        操作方法
        :param direction: 方向
        :return:
        '''
        def move_row_left(row):
            # 吧零散的非零单元挤到一块
            def tighten(row):
                # 除去零单元
                new_row = [i for i in row if i != 0]
                # 补充零担元
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row
            #合并相同数字
            def merge(row):
                pair = False
                new_row = []
                # for i in range(len(row)):
                #     #如果是一对相同的数字，合并
                #     if pair:
                #         new_row.append(2 * row[i])
                #         self.score += 2 * row[i]
                #         pair = False
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        #如果存在一对相同的数字，置pair为true,并且补充0位置
                        if i + 1 < len(row) and row[i] == row[i+1] :
                            pair =True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                #断言new_row长度和row等长，返回
                assert len(new_row) == len(row)
                return new_row
            #返回压缩合并后的一行
            return tighten(merge(tighten(row)))


        moves = {}
        moves['Left']  = lambda field:                              \
                [move_row_left(row) for row in field]
        moves['Right'] = lambda field:                              \
                invert(moves['Left'](invert(field)))
        moves['Up']    = lambda field:                              \
                transpose(moves['Left'](transpose(field)))
        moves['Down']  = lambda field:                              \
                transpose(moves['Right'](transpose(field)))

        # moves = {}
        # #向左操作
        # moves['Left'] = lambda field:   \
        #      [move_row_left(row) for row in field]
        # # 向右操作，即向左的反向挤压
        # moves['Right'] = lambda field:  \
        #      invert(moves['Left'](invert(field)))
        # #向上操作，将矩阵转置成向左操作，然后再转置
        # moves['Up'] = lambda field:     \
        #      transpose(moves['Left'](transpose(field)))
        # #向下操作，将矩阵转置成向右操作，然后再转置
        # moves['Down'] = lambda field:   \
        #      transpose(moves['Right'](transpose(field)))

        #执行方向操作
        # if direction in moves:
        #     #如果操作正确，执行操作
        #     if self.move_is_possible(direction):
        #         self.field = moves[direction](self.field)
        #         #生成新的初始块
        #         self.spawn()
        #         return True
        #     else:
        #         return False
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    #游戏过关
    def is_win(self):
         #比较过关分数
         return any(any(i >= self.win_value for i in row)  for row in self.field)
    #游戏结束
    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)


    def draw(self,screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        def cast(string):
            screen.addstr(string+'\n')
        #画水平分割线
        def draw_hor_separator():
            line = '+'+('+------'*self.width+'+')[1:]
            separator = defaultdict(lambda :line)
            if not hasattr(draw_hor_separator,'counter'):
                draw_hor_separator.counter =0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter += 1
        #画出垂直分割线
        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')
        screen.clear()
        #输出分数
        cast('SCORE: '+str(self.score))
        #输出最高分数
        if 0 != self.highscore:
            cast('HGHSCORE: ' + str(self.highscore))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        #胜利输出YOU WIN!
        if self.is_win():
            cast(win_string)
        else:
            #游戏结束
            if self.is_gameover():
                cast(gameover_string)
            else:
                #帮助
                cast(help_string1)
        cast(help_string2)

    def move_is_possible(self,direction):
        #行可左移动状态
        def row_is_left_movable(row):
            #定义每行移动状态
            def change(i):
                #连续为空，压缩
                if row[i] ==0 and row[i+1]==0:
                    return True
                #连续相同，合并
                if row[i] !=0 and row[i+1]==row[i]:
                    return True
                return False
            #全为0返回False，否则返回True
            return any(change(i) for i in range(len(row)-1))
        checks = {}
        #向左移动状态
        checks['Left'] = lambda field  :                       \
            any(row_is_left_movable(row) for row in field)
        #向右移动状态
        checks['Right'] = lambda field:                        \
            checks['Left'](invert(field))
        #向上移动状态
        checks['Up']    = lambda field:                        \
            checks['Left'](transpose(field))
        #向下移动状态
        checks['Down']  = lambda field:                         \
            checks['Right'](transpose(field))

        #返回方向操作状态
        if direction in checks:
            return checks[direction](self.field)
        else:
            return False



def get_user_action(keyboard):
    '''
    获取用户有效输入
    :param keyboard:
    :return:
    '''
    char = "N"
    while char not in actions_dict:
        char = keyboard.getch()
    return actions_dict[char]


def transpose(field):
    '''
    使用zip函数将矩阵转置
    :param field: 矩阵
    :return: 转置矩阵
    '''
    return [list(row) for row in zip(*field)]


def invert(field):
    '''
    逆转矩阵的每一行
    :param field: 矩阵
    :return: 矩阵
    '''
    return [row[::-1] for row in field]


#主函数
def main(stdscr):
    def init():
        #重置游戏棋盘
        game_field.reset()
        return 'Game'

    #未游戏状态
    def not_game(state):
        #画出Gameover或者win 的界面
        game_field.draw(stdscr)
        #  读取用户输入得到action，判断重启游戏还是结束
        action = get_user_action(stdscr)

        responses = defaultdict(lambda :state) #默认是当前状态，没有行为就在当前一直循环
        responses["Restart"],responses["Exit"] ='Init','Exit' #转换到相应状态
        return responses[action]

    #游戏状态
    def game():
        #画出当前棋盘状态
        game_field.draw(stdscr)
        #读取用户输入得到action
        action = get_user_action(stdscr)

        if action == "Restart":
            return 'Init'
        if action == "Exit":
            return 'Exit'
        #if 成功移动一步
        if game_field.move(action):
            #查看分数
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return  'Gameover'
        return 'Game'


    #状态机对应字典
    state_actions = {
        'Init':init,
        'Win' : lambda :not_game("Win"),
        'Gameover' : lambda: not_game("Gameover"),
        'Game': game
    }

    curses.use_default_colors()
    #新建一个游戏库
    game_field = GameField(win=32)

    state = 'Init'
    #状态机开始循环
    while state != 'Exit':
        state = state_actions[state]()











curses.wrapper(main)





