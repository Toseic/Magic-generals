from random import randint as r

def naive(k,visual_field_list):
    while True:
        i=r(0,49)
        j=r(0,49)
        if len(visual_field_list[i][j][2]) and visual_field_list[i][j][2][0][1] == k:
            return [i, j, visual_field_list[i][j][2][0][0]-1, r(0,3)]