import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

puzzle = {1:[4,0,3,0,8,0,0,6,1],
          2:[0,8,1,7,0,0,4,0,9],
          3:[2,0,0,0,0,0,3,0,0],
          4:[6,9,0,1,7,0,8,0,0],
          5:[3,5,7,2,0,8,1,0,0],
          6:[8,0,2,3,0,0,0,4,5],
          7:[1,3,5,6,0,0,0,0,0],
          8:[0,0,0,5,0,0,0,1,0],
          9:[0,0,6,0,1,0,2,0,7]}

puzzle2 = [(9,5,0, 0,0,8, 0,0,0),
           (0,0,0, 9,7,0, 0,0,1),
           (7,0,4, 0,0,3, 0,0,0),
           
           (0,6,0, 0,0,5, 4,0,0),
           (3,0,0, 0,0,0, 0,0,5),
           (0,0,1, 3,0,0, 0,8,0),
           
           (0,0,0, 2,0,0, 3,0,9),
           (6,0,0, 0,9,1, 0,0,0),
           (0,0,0, 8,0,0, 0,2,7)]

def missing(ls):
    'ls is an array, return list of missing values 1-9'
    return [i for i in range(1,10) if i not in ls]
def dup(ls):
    'ls is an array, return max count'
    vals,cnts = np.unique(ls, return_counts = True)
    return cnts[np.where(vals != 0)].max()
def rc_to_box(r,c):
    return ((c - 1) // 3) + (((r - 1) // 3) * 3) + 1
def identical_pair(ls):
    'return list of duplicated pairs given array of lists'
    vals,cnts = np.unique(ls, return_counts = True)
    return [x for x in vals[np.where(cnts == 2)] if len(x) == 2]
def onlys(ls):
    'return array of unique values from array of lists'
    vals,cnts = np.unique([x for outer in ls for x in outer], return_counts = True)
    return vals[np.where(cnts == 1)]
def drop_extra_bc_pair(pos,pair):
    'return pos with values of pair removed if pos != pair'
    return pos if pos == pair else [x for x in pos if x not in pair]
class Sudoku:
    def __init__(self,s = None):
        if s == None:
            s = np.zeros((9,9))
        else:
            pass
        self.df = pd.DataFrame(s,
                               columns = range(1,10),
                               index = range(1,10),
                               dtype = 'int64')
        self.possible = pd.DataFrame([tuple([list(range(1,10)) for c in range(9)]) for r in range(9)],
                                     columns = range(1,10),
                                     index = range(1,10))
    def row(self,i,kind = 'df'):
        '1 through 9'
        if kind == 'df':
            return self.df.loc[i,:].values
        elif kind == 'possible':
            return self.possible.loc[i,:].values
    def set_row(self,i,val,kind = 'df'):
        'set val to row i'
        if kind == 'df':
            self.df.loc[i,:] = val
        elif kind == 'possible':
            self.possible.loc[i,:] = val
    def col(self,i,kind = 'df'):
        '1 through 9'
        if kind == 'df':
            return self.df.loc[:,i].values
        elif kind == 'possible':
            return self.possible.loc[:,i].values
    def set_col(self,i,val,kind = 'df'):
        'set val to column i'
        if kind == 'df':
            self.df.loc[:,i] = val
        elif kind == 'possible':
            self.possible.loc[:,i] = val
    def box_square(self,i,kind = 'df'):
        ''' 1 2 3
            4 5 6
            7 8 9'''
        r = (((i - 1) // 3) * 3) + 1
        c = (((i - 1) % 3) * 3) + 1
        if kind == 'df':
            return self.df.loc[r:r+2,c:c+2]
        elif kind == 'possible':
            return self.possible.loc[r:r+2,c:c+2]
    def set_box_square(self,i,val,kind = 'df'):
        'set box i to val'
        r = (((i - 1) // 3) * 3) + 1
        c = (((i - 1) % 3) * 3) + 1
        if kind == 'df':
            self.df.loc[r:r+2,c:c+2] = val
        elif kind == 'possible':
            self.possible.loc[r:r+2,c:c+2] = val
    def box(self,i,kind = 'df'):
        return self.box_square(i,kind).values.flatten()
    def miss_row(self,i,kind = 'df'):
        return missing(self.row(i,kind))
    def miss_col(self,i,kind = 'df'):
        return missing(self.col(i,kind))
    def miss_box(self,i,kind = 'df'):
        return missing(self.box(i,kind))
    def trim_possible(self):
        'remove impossible for unknown values inplace'
        updated = False
        for m in range(1,10):
            for n in range(1,10):
                if self.df.loc[m,n] == 0:
                    cur = self.possible.loc[m,n]
                    mem = cur.copy()
                    cur = [x for x in cur if x in self.miss_row(m)]
                    cur = [x for x in cur if x in self.miss_col(n)]
                    cur = [x for x in cur if x in self.miss_box(rc_to_box(m,n))]
                    self.possible.loc[m,n] = cur
                    if mem != cur:
                        updated = True
                else:
                    self.possible.loc[m,n] = [self.df.loc[m,n]]
        return updated
    def check(self):
        for i in range(1,10):
            if dup(self.row(i)) > 1:
                return False
            if dup(self.col(i)) > 1:
                return False
            if dup(self.box(i)) > 1:
                return False
        return True
    def set_possible_one(self):
        'if there is only one possible value for an unknown set it'
        for m in range(1,10):
            for n in range(1,10):
                if self.df.loc[m,n] == 0:
                    if len(self.possible.loc[m,n]) == 1:
                        self.df.loc[m,n] = self.possible.loc[m,n][0]
    def set_hanging(self):
        'if a number is only possible in one square of a row or column use it'
        for r in range(1,10):
            for val in onlys(self.row(r,'possible')):
                self.set_row(r,[val if (ent == 0) and (val in pos) else ent for ent,pos in zip(self.row(r),self.row(r,'possible'))])
        for c in range(1,10):
            for val in onlys(self.col(c,'possible')):
                self.set_col(c,[val if (ent == 0) and (val in pos) else ent for ent,pos in zip(self.col(c),self.col(c,'possible'))])
        for b in range(1,10):
            for val in onlys(self.box(b,'possible')):
                self.set_box_square(b,self.box_square(b,'possible').applymap(lambda pos:[val] if val in pos else pos),'possible')        
    
    def pair_pair_trim(self):
        'if there are two identical pairs in same eliminate others'
        mem = self.possible.copy()
        for r in range(1,10):
            for pair in identical_pair(self.row(r,'possible')):
                self.set_row(r,[drop_extra_bc_pair(pos,pair) for pos in self.row(r,'possible')],'possible')
        for c in range(1,10):
            for pair in identical_pair(self.col(c,'possible')):
                self.set_col(c,[drop_extra_bc_pair(pos,pair) for pos in self.col(c,'possible')],'possible')
        for b in range(1,10):
            for pair in identical_pair(self.box(b,'possible')):
                self.set_box_square(b,self.box_square(b,'possible').applymap(lambda pos:drop_extra_bc_pair(pos,pair)),'possible') 
        return (mem != self.possible).any().any() #True if any values are different
    def rec_solve(self):
        cnt = 0
        while True:
            if not (self.trim_possible() or self.pair_pair_trim()):
                break
            self.set_possible_one()
            cnt += 1
        return cnt
    
A = Sudoku(puzzle2)
print(A.df)
print(A.rec_solve())
#with pd.option_context('display.width',200,'max_columns',200):
#    print(A.possible)
A.pair_pair_trim()
A.set_hanging()
print(A.rec_solve())
print(A.df)
print(A.check())

