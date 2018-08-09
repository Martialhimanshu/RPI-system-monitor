# a = [10,3,6,8,9,4,3]
# x= 12

# Create your tests here.
# def keyPair(a,x):
#     if len(a)<0:
#         return
#     for i in range(len(a)-1):
#         for j in range(1,len(a)):
#             if a[i] + a[j] == x:
#                 print('yes list contains sum of element for pair', (a[i],a[j]))
#             else:
#                 pass
#
# keyPair(a,x)


# def maxDiff(a):
#     max = 0
#     result = 0
#     if len(a)<0:
#         return 0
#     for i in range(len(a)-1,0,-1):
#         if a[i] > max:
#             max = a[i]
#         temp = max - a[i]
#         if temp > result:
#             result = temp
#     print(result)
# maxDiff(a)
#
# def maxDiff1(a):
#     return max(a)-min(a)
# print(maxDiff1(a))


def TicTacToe():

    def printboard():
        print(choices[0] + '|' + choices[1] + '|' + choices[2])
        print("------------")
        print(choices[3] + '|' + choices[4] + '|' + choices[5])
        print("------------")
        print(choices[6] + '|' + choices[7] + '|' + choices[8])


    choices = []
    for x in range(0,9):
        choices.append(str(x+1))
    player1 = True
    winner = False


    while not winner:
        printboard()

        if player1:
            print("Player 1:")
        else:
            print("player 2:")
        try:
            choice=int(input("Enter your choice: "))
        except:
            print("Enter Valid choice: ")
            continue
        if choices[choice-1] == 'X' or choices[choice-1] == 'O':
            print("Enter valid choice, bcoz your choice is matching with other player")
            continue
        if player1:
            choices[choice-1] = 'X'
        else:
            choices[choice-1] = 'O'
        player1 = not player1


        if ((choices[0] == choices[4] and choices[0] == choices[8]) or
                (choices[2] == choices[4] and choices[4] == choices[6]) or
                (choices[0] == choices[3] and choices[3] == choices[6]) or
                (choices[0] == choices[1] and choices[1] == choices[2]) or
                (choices[1] == choices[4] and choices[4] == choices[7])):
            winner = True
    printboard()
    print ("Player " + str(int(player1)) + " wins!\n")



TicTacToe()




















