'''
Approved for Public Release: 12-3351. Distribution Unlimited
			(c)2012-The MITRE Corporation. 
Licensed under the Apache License, Version 2.0 (the "License");
			you may not use this file except in compliance with the License.
			You may obtain a copy of the License at
			http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
'''

#import pstat               # required 3rd party module
import math, copy#, string  # required python modules
#from types import *

def tiecorrect(rankvals):
    """
    Corrects for ties in Mann Whitney U and Kruskal Wallis H tests.  See
    Siegel, S. (1956) Nonparametric Statistics for the Behavioral Sciences.
    New York: McGraw-Hill.  Code adapted from |Stat rankind.c code.

    Usage:   ltiecorrect(rankvals)
    Returns: T correction factor for U or H
    """
    sorted,posn = shellsort(rankvals)
    n = len(sorted)
    T = 0.0
    i = 0
    while (i<n-1):
        if sorted[i] == sorted[i+1]:
            nties = 1
            while (i<n-1) and (sorted[i] == sorted[i+1]):
                nties = nties +1
                i = i +1
            T = T + nties**3 - nties
        i = i+1
    T = T / float(n**3-n)
    return 1.0 - T

def shellsort(inlist):
    """
    Shellsort algorithm.  Sorts a 1D-list.

    Usage:   lshellsort(inlist)
    Returns: sorted-inlist, sorting-index-vector (for original list)
    """
    n = len(inlist)
    svec = copy.deepcopy(inlist)
    ivec = range(n)
    gap = n/2   # integer division needed
    while gap >0:
        for i in range(gap,n):
            for j in range(i-gap,-1,-gap):
                while j>=0 and svec[j]>svec[j+gap]:
                    temp        = svec[j]
                    svec[j]     = svec[j+gap]
                    svec[j+gap] = temp
                    itemp       = ivec[j]
                    ivec[j]     = ivec[j+gap]
                    ivec[j+gap] = itemp
        gap = gap / 2  # integer division needed
    # svec is now sorted inlist, and ivec has the order svec[i] = vec[ivec[i]]
    return svec, ivec

def chisqprob(chisq,df):
    """
    Returns the (1-tailed) probability value associated with the provided
    chi-square value and df.  Adapted from chisq.c in Gary Perlman's |Stat.

    Usage:   lchisqprob(chisq,df)
    """
    BIG = 20.0
    def ex(x):
        BIG = 20.0
        if x < -BIG:
            return 0.0
        else:
            return math.exp(x)

    if chisq <=0 or df < 1:
        return 1.0
    a = 0.5 * chisq
    if df%2 == 0:
        even = 1
    else:
        even = 0
    if df > 1:
        y = ex(-a)
    if even:
        s = y
    else:
        s = 2.0 * zprob(-math.sqrt(chisq))
    if (df > 2):
        chisq = 0.5 * (df - 1.0)
        if even:
            z = 1.0
        else:
            z = 0.5
        if a > BIG:
            if even:
                e = 0.0
            else:
                e = math.log(math.sqrt(math.pi))
            c = math.log(a)
            while (z <= chisq):
                e = math.log(z) + e
                s = s + ex(c*z-a-e)
                z = z + 1.0
            return s
        else:
            if even:
                e = 1.0
            else:
                e = 1.0 / math.sqrt(math.pi) / math.sqrt(a)
            c = 0.0
            while (z <= chisq):
                e = e * (a/float(z))
                c = c + e
                z = z + 1.0
            return (c*y+s)
    else:
        return s

def rankdata(inlist):
    """
    Ranks the data in inlist, dealing with ties appropritely.  Assumes
    a 1D inlist.  Adapted from Gary Perlman's |Stat ranksort.

    Usage:   lrankdata(inlist)
    Returns: a list of length equal to inlist, containing rank scores
    """
    n = len(inlist)
    svec, ivec = shellsort(inlist)
    sumranks = 0
    dupcount = 0
    newlist = [0]*n
    for i in range(n):
        sumranks = sumranks + i
        dupcount = dupcount + 1
        if i==n-1 or svec[i] <> svec[i+1]:
            averank = sumranks / float(dupcount) + 1
            for j in range(i-dupcount+1,i+1):
                newlist[ivec[j]] = averank
            sumranks = 0
            dupcount = 0
    return newlist

def lkruskalwallish(*args):
    """
    The Kruskal-Wallis H-test is a non-parametric ANOVA for 3 or more
    groups, requiring at least 5 subjects in each group.  This function
    calculates the Kruskal-Wallis H-test for 3 or more independent samples
    and returns the result.  

    Usage:   lkruskalwallish(*args)
    Returns: H-statistic (corrected for ties), associated p-value
    """
    args = list(args)
    n = [0]*len(args)
    all = []
    n = map(len,args)
    for i in range(len(args)):
        all = all + args[i]
    ranked = rankdata(all)
    T = tiecorrect(ranked)
    for i in range(len(args)):
        args[i] = ranked[0:n[i]]
        del ranked[0:n[i]]
    rsums = []
    for i in range(len(args)):
        rsums.append(sum(args[i])**2)
        rsums[i] = rsums[i] / float(n[i])
    ssbn = sum(rsums)
    totaln = sum(n)
    h = 12.0 / (totaln*(totaln+1)) * ssbn - 3*(totaln+1)
    df = len(args) - 1
    if T == 0:
        print "All numbers identical!"
        return 0, 1
    h = h / float(T)
    return h, chisqprob(h,df)


'''
def akruskalwallish(*args):
    """
    The Kruskal-Wallis H-test is a non-parametric ANOVA for 3 or more
    groups, requiring at least 5 subjects in each group.  This function
    calculates the Kruskal-Wallis H and associated p-value for 3 or more
    independent samples.
    
    Usage:   akruskalwallish(*args)     args are separate arrays for 3+ conditions
    Returns: H-statistic (corrected for ties), associated p-value
    """
    assert len(args) == 3, "Need at least 3 groups in stats.akruskalwallish()"
    args = list(args)
    n = [0]*len(args)
    n = map(len,args)
    all = []
    for i in range(len(args)):
        all = all + args[i].tolist()
    ranked = rankdata(all)
    T = tiecorrect(ranked)
    for i in range(len(args)):
        args[i] = ranked[0:n[i]]
        del ranked[0:n[i]]
    rsums = []
    for i in range(len(args)):
        rsums.append(sum(args[i])**2)
        rsums[i] = rsums[i] / float(n[i])
    ssbn = sum(rsums)
    totaln = sum(n)
    h = 12.0 / (totaln*(totaln+1)) * ssbn - 3*(totaln+1)
    df = len(args) - 1
    if T == 0:
        raise ValueError, 'All numbers are identical in akruskalwallish'
    h = h / float(T)
    return h, chisqprob(h,df)
'''