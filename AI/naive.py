from random import randint as r

def naive(k,l,w,visual_field_list):
    while True:
        i=r(0,l-1)
        j=r(0,w-1)
        if len(visual_field_list[i][j][2]) and visual_field_list[i][j][2][0][1] == k:
            d = r(0,3)
            if d == 0:
                m, n = i-1, j
            elif d == 1:
                m, n = i, j-1
            elif d == 2:
                m, n = i+1, j
            elif d == 3:
                m, n = i, j+1
            return [i, j, r(0,1), m, n]