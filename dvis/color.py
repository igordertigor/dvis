#!/usr/bin/env python

import matplotlib.colors

__all__ = ["cmix","col3","col4"]

col3 = [(float(x)/255,float(y)/255,float(z)/255) for x,y,z in \
        [(25,25,112),(255,69,0),(200,255,255)] ]
col4 = [(float(x)/255,float(y)/255,float(z)/255) for x,y,z in \
        [(25,25,112),(34,139,34),(255,215,0),(240,255,255)] ]

def cmix ( c1, c2, ratio ):
    """mix two colors with

    :Parameters:
        *c1*
            first color
        *c2*
            second color
        *ratio*
            amount c1/amount c2

    :Return:
        a mix of the two colors
    """
    p = float(ratio)/(1+ratio)
    q = 1-p

    # Make sure that both colors are lists
    c1 = __mkcolorlist ( c1 )
    c2 = __mkcolorlist ( c2 )

    return [p*_1 + q*_2 for _1,_2 in zip ( c1,c2 )]

def colorsequence ( c ):
    """Make sure the entries in c can be interpreted as a sequence
    so that iterating of c gives a sequence of rgb tuples in turn"""
    if matplotlib.colors.is_color_like ( c ):
        return [matplotlib.colors.colorConverter.to_rgb ( c )]
    out = []
    if hasattr ( c, '__iter__' ):
        for c_ in c:
            out += colorsequence ( c_ )
    return out


def __mkcolorlist ( c ):
    if isinstance ( c, list ):
        out = c
    elif getattr ( c, '__iter__', False ):
        out = list ( c )
    elif isinstance ( c, (float,int) ):
        out = [float(c)]*3

    assert len(out) == 3, "colors should have length 3"

    return out
