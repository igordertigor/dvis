#!/usr/bin/env python

import matplotlib.colors
import pylab as pl

__all__ = ["cmix","col3","col4","luminancecode"]

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

def luminancecode ( x, basecolor, **kwargs ):
    """Create a code for the values in x

    :Parameters:
        *x*
            values to be coded
        *basecolor*
            basic color that should be mixed with white for lower values

    :Optional Keyword Arguments:
        *vmin*
            minimum of color scale (default: min(x))
        *vmax*
            maximum of color scale (default: max(x))
        *mincol*
            minimum color concentration (default: 0.1)
    """
    vmin = float(kwargs.setdefault ( 'vmin', min(x) ))
    vmax = float(kwargs.setdefault ( 'vmax', max(x) ))
    mincol = float(kwargs.setdefault('mincol', 0.1 ))

    ratios = pl.clip(((vmax-x)/(vmax-vmin)),0,1e8)/mincol

    return [cmix('w',basecolor,r) for r in ratios]

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
    if matplotlib.colors.is_color_like ( c ):
        return list(matplotlib.colors.colorConverter.to_rgb(c))
    else:
        print c
        raise ValueError, "c cannot be converted to a color"
