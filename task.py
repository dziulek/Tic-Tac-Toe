import numpy as np

def main():

    input = "kootttteeekk"

    letter = '`'

    idx = 0

    l = []
    letters_blocks = []
    cnt = 0

    for i in range(len(input)):
    
        if input[i] != letter:
            if len(l) > 0:
                l[-1] += cnt
            l.append(1)
            cnt = 0
            letter = input[i]
            letters_blocks.append(letter)
        
        else:
            cnt += 1

    l[-1] += cnt

    tmp = []
    for i in range(len(l)):

        tmp += [letters_blocks[i], str(l[i])]

    print(''.join(tmp))


if __name__ == "__main__":

    main()