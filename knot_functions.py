import numpy as np
import re
import random

# cleans str and returns numpy array
def clean_k_arc(k_str):
    try:
        matches = re.compile(r'\d+').findall(k_str)
        nums = np.array([int(match) for match in matches])
        arc = nums.reshape(int(nums.shape[0]/2),2)
        arc_xoco(xo_arc(arc))
        0/arc.shape[0]
        return arc
    except:
        return None
    
# turns an arc array into a xo array
def xo_arc(arc):
    s = np.shape(arc)[0]
    xo = np.zeros([s,s], dtype=int)
    for i in range(s):
        for j in range(2):
            ik = i+1
            ij = arc[i,j]-1
            xo[-ik, ij] = j+1
    return xo

# turns a xo array into a xco array
def xco_xo(xo):
    xco = xo.copy()
    s = np.shape(xo)[0]
    r = range(1,s-1)
    for i in r:
        for j in r:
            if xo[i,j] == 0:
                hlz, hrz = np.count_nonzero(xo[i,:j]), np.count_nonzero(xo[i,j+1:])
                vuz, vdz = np.count_nonzero(xo[:i,j]), np.count_nonzero(xo[i+1:,j])
                if hlz==1 and hrz==1 and vuz==1 and vdz==1:
                    xco[i,j] = 3
    return xco

# turns an arc array into a xco array
def xco_arc(arc):
    return(xco_xo(xo_arc(arc)))

# turns a xo or xco array into an arc array
def arc_xoco(xoco):
    s = np.shape(xoco)[0]
    arc = np.zeros([s,2], dtype=int)
    for i in range(s):
        ik = i+1
        j1 = int(np.where(xoco[-ik]==1)[0])+1
        j2 = int(np.where(xoco[-ik]==2)[0])+1
        arc[i,0], arc[i,1] = j1, j2
    return arc

# turns a xco array into a a xabo array
def xabo_xco(xco, crossings):
    xabo = xco.copy()
    cruces = np.array(np.where(xabo==3))
    xabo[cruces[0],cruces[1]] = crossings
    return xabo


# get circle coords and circle codes
def circles_crd_cds(xabo):
    size = np.shape(xabo)[0]
    crossings = np.array(np.where(xabo>3))

    n_crossings = np.shape(crossings)[1]
    cr_check = np.zeros((n_crossings*2), dtype=int) #cross_check

    # 4 = A -> (up-right)(down-left)
    # 5 = B -> (up-left)(down-right)
    # cr_check = [c1u, c1d, c2u, c2d, ..., cnu, cnd]

    # CODES False=vertex ; True=crossing
    # p = position = [[coords in matrix], is_horizontal_bool, is_increasing_bool]

    circle_coords, circle_codes = [], []
    n_circle = 0

    while np.any(cr_check==0):
        circle_coords.append([])
        circle_codes.append([])
        fz= np.where(cr_check==0)[0][0] #first_zero
        p = [[crossings[:,int(fz/2)][0], crossings[:,int(fz/2)][1]], False, fz%2!=0]
        p0 = p[:]
        while True:
            circle_coords[n_circle].append(p[0])
            for i in range(1, size):
                r, c = 0, 0
                if not(p[2]): i=-i

                if p[1]: c = i
                else: r = i

                px = xabo[p[0][0]+r, p[0][1]+c]
                if px != 0:
                    # update p0 & p1
                    p[0], p[1] = [p[0][0]+r, p[0][1]+c], not(p[1])
                    break 
            
            # update p2 & codes
            if px==1 or px==2:
                line = xabo[p[0][0],:] if p[1] else xabo[:,p[0][1]]
                coord = p[0][1] if p[1] else p[0][0]
                p[2] = False if any(line[:coord]!=0) else True
                circle_codes[n_circle].append(False)
            elif px==5: p[2] = not(p[2])
            
            # update cr_check & codes
            if px==4 or px==5:
                circle_codes[n_circle].append(True)
                for i in range(n_crossings):
                    if all(p[0]==crossings[:,i]):
                        if not(p[1]) or px==5:
                            if p[2]: cr_check[2*i+1]=1
                            else: cr_check[2*i]=1
                        else:
                            if p[2]: cr_check[2*i]=1
                            else: cr_check[2*i+1]=1
                        break

            if np.all(p==p0): break

        n_circle += 1

    for i in range(n_circle):
        circle_codes[i] = [circle_codes[i][-1]] + circle_codes[i][:-1]
        
    return circle_coords, circle_codes


######################
# GENERATE NEW KNOTS #
######################
def state_is_valid(state, n, pos):
    if np.count_nonzero(state>0)==2*n-1:
        sol = state.copy()
        sol[0, pos[1]] = 2
        xco_sol = xco_xo(sol)
        if np.count_nonzero(xco_sol==3)>n-1:
            return True

    return False

def get_candidates(state, n, pos):
    p = state[pos]
    cands = []
    if p == 1:
        for i in range(1, n):
            if np.count_nonzero(state[i,:]==2)==0:
                cands.append([(i, pos[1]), 2])
    elif p == 2:
        for j in range(n):
            if np.count_nonzero(state[:,j]==1)==0:
                cands.append([(pos[0], j), 1])
    return cands

def search(state, n, pos):
    if state_is_valid(state, n, pos):
        state[0, pos[1]] = 2
        return xco_xo(state)
    else:
        candidates = get_candidates(state, n, pos)
        random.shuffle(candidates)
        for candidate in candidates:
            state[candidate[0]] = candidate[1]
            if type(search(state, n, candidate[0]))!=type(None):
                return xco_xo(state)
            else:
                state[candidate[0]] = 0


def random_knot(n):
    solutions = []
    state = np.zeros((n,n), dtype=np.int8)
    pos = (0, random.randint(0,n-1))
    state[pos]=1
    return search(state, n, pos)
