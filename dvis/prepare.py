#!/usr/bin/env python

__doc__ = """Prepare a figure for plotting"""

__all__ = ["prepare_axes","axes_grid"]

import pylab as pl
import mpl_toolkits.axes_grid as agrid
import mpl_toolkits.axes_grid.axes_size as Size
import re

import warnings
spineswarning = """your axes object does not support spines.
The most probable reason for this is that you are using an old version of matplotlib.
spines allow for more beautiful plots and are a new feature in matplotlib 1.0.0.
"""

def prepare_axes ( ax, haveon=('b','l'), out=10 ):
    """Prepare an axes object to have axes offset

    :Parameters:
        *axes*
            the axes object
        *haveon*
            a list of the spines that should be shown
        *out*
            amount by which the spines should be moved outward

    :Return:
        the prepared axes object
    """
    if getattr(ax, '__iter__', False ):
        return [prepare_axes ( ax_ ) for ax_ in ax]
    # Complete haveon
    splon = []
    for loc in haveon:
        m = re.search ( loc+".*", "bottom\nleft\nright\ntop\n" )
        if not m is None:
            splon.append ( m.group(0) )

    if getattr ( ax, 'spines', False ):
        for loc,spine in ax.spines.iteritems():
            if loc in splon:
                spine.set_position ( ('outward', out) )
            else:
                spine.set_color ( 'none' )
    else:
        warnings.warn ( spineswarning, DeprecationWarning )

    # Now remove unwanted ticks
    if 'bottom' in splon:
        ax.xaxis.set_ticks_position ( 'bottom' )
    elif 'top' in splon:
        ax.xaxis.set_ticks_position ( 'top' )
    else:
        ax.xaxis.set_ticks_position ( 'none' )
        ax.xaxis.set_ticklabels ( '' )

    if 'left' in splon:
        ax.yaxis.set_ticks_position ( 'left' )
    elif 'right' in splon:
        ax.yaxis.set_ticks_position ( 'right' )
    else:
        ax.yaxis.set_ticks_position ( 'none' )
        ax.yaxis.set_ticklabels ( '' )

    return ax

def axes_grid ( naxes, **kwargs ):
    """shortcut to the axes grid of pylab

    :Parameters:
        *naxes*
            a tuple of x,y counts of axes to be generated

    :Optional Keyword Arguments:
        *fig*
            figure instance to use (Default: pl.gcf())
        *rect*
            plotting rectange (Default: .05,.05,.9,.9)
        *horz*
            horizontal cell sizes (Default: One Scaled(1.) field for each
            plot with Fixed(hdist) fields in between)
        *hdist*
            pad horizontally between actual plot boxes with fields of
            fixed size hdist (Default: 0.2)
        *vert*
            vertical cell sizes (Default: One Scaled(1.) field for each
            plot with Fixed(vdist) fields in between)
        *vdist*
            pad vertically between actual plot boxes with fields of fixed
            size vdist (Default: 0.2)
        *nx*
            array with shape naxes that gives the nx arguments for
            divide.new_locator
        *ny*
            array with shape naxes that gives the ny arguments for
            divide.new_locator
        *nx1*
            array with shape naxes that gives the nx1 arguments for
            divide.new_locator
        *ny1*
            array with shape naxes that gives the ny1 arguments for
            divide.new_locator

    :Returns:
        an array of axes objects with shape naxes
    """

    # Parsing input and setting defaults
    fig   = kwargs.setdefault ( 'fig', pl.gcf() )
    rect  = kwargs.setdefault ( 'rect', [.05,.05,.9,.9] )
    horz  = kwargs.setdefault ( 'horz',
            [Size.Scaled(1.) for i in xrange(naxes[0])] )
    vert  = kwargs.setdefault ( 'vert',
            [Size.Scaled(1.) for i in xrange(naxes[1])] )
    hdist = kwargs.setdefault ( 'hdist', 0.2 )
    vdist = kwargs.setdefault ( 'vdist', 0.2 )

    if hdist>0:
        for i in xrange ( naxes[0]-1 ):
            horz.insert ( 2*i+1, Size.Fixed(hdist) )
        hslice = slice ( 0, len(horz), 2 )
    else:
        hslice = slice ( 0, len(horz) )
    if vdist>0:
        for i in xrange ( naxes[1]-1 ):
            vert.insert ( 2*i+1, Size.Fixed(vdist) )
        vslice = slice ( 0, len(vert), 2 )
    else:
        vslice = slice ( 0, len(vert) )

    nx  = kwargs.setdefault ( 'nx',  pl.mgrid[hslice,vslice][0] )
    ny  = kwargs.setdefault ( 'ny',  pl.mgrid[hslice,vslice][1] )
    nx1 = kwargs.setdefault ( 'nx1', pl.array([[None]*naxes[1]]*naxes[0]) )
    ny1 = kwargs.setdefault ( 'ny1', pl.array([[None]*naxes[1]]*naxes[0]) )

    # This is actually placing the axes
    divider = agrid.Divider ( fig, rect, horz, vert, aspect=False )
    ax = pl.array([ fig.add_axes ( rect, label='%d'%i ) \
            for i in xrange ( naxes[0]*naxes[1] ) ])
    ax.shape = naxes
    for i in xrange ( naxes[0] ):
        for j in xrange ( naxes[1] ):
            # print nx[i,j],ny[i,j]
            ax[i,j].set_axes_locator(
                    divider.new_locator(nx=nx[i,j],nx1=nx1[i,j],
                        ny=ny[i,j],ny1=ny1[i,j])
                    )
    return ax
