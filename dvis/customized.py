#!/usr/bin/env python

import pylab as pl
from matplotlib.artist import Artist
from matplotlib.collections import LineCollection
from matplotlib.ticker import FormatStrFormatter

import dvis.color

__all__ = ["Scatter","Boxplot","Errorline"]

def Scatter ( x, y, ax=None, **kwargs ):
    """Creates a Tufte scatter plot

    :Parameters:
        *x,y*
            x and y values of the scatter plot
        *ax*
            target axes (defaults to gca())

    :Optional keyword arguments:
        See pylab.scatter
    """
    if ax is None:
        ax = pl.gca()
    ax.add_artist ( RangeFrameArtist ( x, y ) )
    ax.set_frame_on ( False )
    S = ax.scatter ( x, y, **kwargs )
    ax.tick_params ( labelsize=8 )
    ax.get_xaxis().set_major_formatter ( FormatStrFormatter ( "%.3f" ) )
    ax.get_yaxis().set_major_formatter ( FormatStrFormatter ( "%.3f" ) )
    return S

def Boxplot ( x, ax=None, offset=0.005, **kwargs ):
    """Creates a Tufte boxplot

    :Parameters:
        *x*
            values to be summarized
        *ax*
            target axes
        *offset*
            offset to mark central part and median gap

    :Optional keyword arguments:
        See pylab.boxplot
    """
    if ax is None:
        ax = pl.gca()
    # call a boxplot and manipulate it
    # how to get the offset right?
    if hasattr (x,'shape'):
        if len(x.shape)==1:
            if hasattr(x[0], 'shape'):
                x = list(x)
            else:
                x = [x,]
        elif len(x.shape) == 2:
            nr, nc = x.shape
            if nr==1:
                x = [x]
            elif nc==1:
                x = [x.ravel()]
            else:
                x = [x[:,i] for i in xrange(nc)]
        else:
            raise ValueError, "input x can have no more than 2 dimensions"
    if not hasattr(x[0],'__len__'):
        x = [x]

    positions = kwargs.setdefault ( 'positions', range(1,len(x)+1) )
    pdist = max(positions)-min(positions)
    offs = 0.5*float(pdist)/len(positions)

    if kwargs.setdefault('vert', 0 ) == 1:
        ax.set_ylim ( positions[0]-offs, positions[-1]+offs )
        ax.set_yticks ( positions )
    else:
        ax.set_xlim ( positions[0]-offs, positions[-1]+offs )
        ax.set_xticks ( positions )

    c = kwargs.setdefault ( 'color', [0,0,0] )
    c = dvis.color.colorsequence ( c )

    for i,pos in enumerate ( positions ):
        d = pl.ravel(x[i])
        kwargs['color'] = c[i%len(c)]
        ax.add_artist (
                BoxplotArtist ( pos,
                    calculate_boxplot_stats ( d, **kwargs ),
                    offset,
                    **kwargs ) )

def Errorline ( x, y, e=None, se=None, ax=None, **kwargs ):
    """Creates a line with a filled error region

    :Parameters:
        *x*
            x values of the line
        *y*
            y values of the line. If y.shape == 2, then se is called for
            every sample of y to derive an upper and lower limit
        *e*
            error (in y direction) This could take either a scalar giving the
            (constant) error, an array of scalar errors, or an array of
            observations. In the latter case, se is applied to every sample
            of e
        *se*
            function that takes a sample and gives the upper and lower sample
        *ax*
            target axes

    :Optional Keyword Arguments:
        are passed to pylab.plot and to pylab.fill
    """
    c = dvis.color.colorsequence ( kwargs.setdefault ( 'color', [0,0,0]))[0]
    kwargs.setdefault ( 'edgecolor', dvis.color.cmix ( c, 'w', 3 ) )
    kwargs.setdefault ( 'facecolor', dvis.color.cmix ( c, 'w', 1.5 ) )
    if se is None:
        se = lambda x: (pl.mean(x)-pl.std(x)/pl.sqrt(len(x)),pl.mean(x)+pl.std(x)/pl.sqrt(len(x)))
    if ax is None:
        ax = pl.gca()

    x = pl.array(x)
    y = pl.array(y)
    if len(y.shape)==1:
        assert len(y.ravel())==len(x.ravel())
        if e is None:
            e = 0.
            ye = pl.concatenate ( (y-e,(y+e)[::-1]) )
        elif isinstance ( e, float ):
            ye = pl.concatenate ( (y-e,(y+e)[::-1]) )
        elif len(e.shape)==1:
            assert len(y.ravel())==len(e.ravel())
            ye = pl.concatenate ( (y-e,(y+e)[::-1]) )
        elif len(e.shape)==2:
            if 2 in e.shape:
                if e.shape[0] == 2:
                    e = e.T
                ye = pl.concatenate ( (e[:,0],e[::-1,1]) )
            else:
                ye1,ye2 = pl.zeros(e.shape[0],'d'),pl.zeros(e.shape[0],'d')
                for i in xrange ( y.shape[0] ):
                    ye1[i],ye2[i] = se(e[i,:])
                ye = pl.concatenate ( (ye1,ye2[::-1]) )
    else:
        # Errors
        if e is None:
            if y.shape[1] == len(x.ravel()):
                y = y.T
            ye1,ye2 = pl.zeros(y.shape[0],'d'),pl.zeros(y.shape[0],'d')
            for i in xrange ( y.shape[0] ):
                ye1[i],ye2[i] = se(y[i,:])
            ye = pl.concatenate ( (ye1,ye2[::-1]) )
            y = pl.mean(y,1)
        else:
            raise ValueError,"y has more than one value per datapoint but e is specified"

    try:
        l = ax.plot ( x, y, **kwargs )
    except TypeError:
        l = ax.plot ( x, y )
        for k,v in kwargs.iteritems ():
            funcName = "set_"+k
            if hasattr(l[0],funcName):
                func = getattr(l[0],funcName)
                func(v)

    f = ax.fill ( pl.concatenate ( (x,x[::-1]) ), ye, **kwargs )
    return l,f

def Errorline_faded ( x, y, e, al, **kwargs ):
    """An Errorline that fades

    Similar to an Error line but fades out according to al.
    IMPORTANT: This line is going to be made up of lots of small lines and
    small rectangular patches.

    :Parameters:
        *x*
            x values of the line
        *y*
            y values of the line. If y.shape == 2, then se is called for
            every sample of y to derive an upper and lower limit
        *e*
            error (in y direction) This could take either a scalar giving the
            (constant) error, an array of scalar errors, or an array of
            observations. In the latter case, se is applied to every sample
            of e
        *al*
            alpha values for the different line segments
        *color*,*edgecolor*,*facecolor*,*ax*
            see Errorline()
    """
    c = dvis.color.colorsequence ( kwargs.setdefault ( 'color', [0,0,0]))[0]
    kwargs.setdefault ( 'edgecolor', dvis.color.cmix ( c, 'w', 3 ) )
    kwargs.setdefault ( 'facecolor', dvis.color.cmix ( c, 'w', 1.5 ) )
    ax = kwargs.setdefault ( 'ax', pl.gca() )

    fade = pl.convolve ( [.5,.5], al, 'valid' )
    yup = y+e
    ydown = y-e
    n = len(fade)
    l,f = [],[]
    for i in xrange ( n ):
        f += ax.fill (
                pl.concatenate((x[i:i+2],x[i+1:i-1:-1])),
                pl.concatenate((yup[i:i+2],ydown[i+1:i-1:-1])),
                ec='none', fc=kwargs['facecolor'], alpha=fade[i] )
        l += ax.plot ( x[i:i+2], y[i:i+2], color=c, alpha=fade[i] )

    return l,f

#################################################################

def calculate_boxplot_stats ( x, **kwargs ):
    whis = kwargs.setdefault ( 'whis', 1.5 )
    bootstrap = kwargs.setdefault ( 'bootstrap', None )

    # Get median and quartiles
    q1,med,q3 = pl.prctile (x, [25,50,75] )
    # Get high extreme
    iq = q3-q1
    hi_val = q3+whis*iq
    wisk_hi = pl.compress ( x<=hi_val, x )
    if len(wisk_hi)==0:
        wisk_hi = q3
    else:
        wisk_hi = max(wisk_hi)
    # Get low extreme
    lo_val = q1-whis*iq
    wisk_lo = pl.compress ( x>=lo_val, x )
    if len(wisk_lo)==0:
        wisk_lo = q3
    else:
        wisk_lo = min(wisk_lo)

    # Get fliers
    flier_hi = pl.compress ( x>wisk_hi, x )
    flier_lo = pl.compress ( x<wisk_lo, x )

    if bootstrap is not None:
        # Do a bootstrap estimate of notch locations
        def bootstrapMedian ( data, N=5000 ):
            # determine 95% confidence intervals of the median
            M = len(data)
            percentile = [2.5,97.5]
            estimate = pl.zeros(N)
            for n in xrange (N):
                bsIndex = pl.randint ( 0, M, M )
                bsData = data[bsIndex]
                estimate[n] = pl.prctile ( bsData, 50 )
            CI = pl.prctile ( estimate, percentile )
            return CI
        CI = bootstrapMedian ( x, N=bootstrap )
        notch_max = CI[1]
        notch_min = CI[0]
    else:
        # Estimate notch locations using Gaussian-based asymptotic
        # approximation
        #
        # For discussion: McGill, R., Tukey, J.W., and
        # Larsen, W.A. (1978) "Variations of Boxplots", The
        # American Statistitian, 32:12-16
        notch_max = med + 1.57*iq/pl.sqrt(len(x))
        notch_min = med - 1.57*iq/pl.sqrt(len(x))
    return {'main':(wisk_lo,q1,med,q3,wisk_hi),
            'fliers':(flier_lo,flier_hi),
            'notch':(notch_min,notch_max)}

class BoxplotArtist ( Artist ):
    def __init__ ( self, x, boxstats, offset, **kwargs ):
        Artist.__init__ ( self )
        self.x = x
        self.boxstats = boxstats
        self.notch = kwargs.setdefault ( 'notch', 0 )
        self.vert = kwargs.setdefault ( 'vert', 0 )
        self.color = kwargs.setdefault ( 'color', [0,0,0] )
        self.offset = offset
        self.lw    = kwargs.setdefault ( 'linewidth', 1 )

    def draw ( self, renderer, *args, **kwargs ):
        if not self.get_visible(): return

        box,pt,dummy = self.make_box_plot()
        dummy.draw(renderer)
        pt.draw(renderer)
        box.draw(renderer)

    def make_box_plot (self):
        x = self.x
        rx = self.axes.get_xlim()
        ry = self.axes.get_ylim()
        ex = self.offset*(rx[1]-rx[0])
        ey = self.offset*(ry[1]-ry[0])
        if self.vert == 1:
            ex,ey = ey,ex
        p = self.boxstats['main']
        n = self.boxstats['notch']
        f_lo,f_hi = self.boxstats['fliers']
        if self.notch:
            lines = [ [(x,p[0]),(x,p[1])],
                    [(x+ex,p[1]),(x+ex,n[0])],
                    [(x+ex,n[0]),(x-ex,p[2]-ey)],
                    [(x-ex,p[2]+ey),(x+ex,n[1])],
                    [(x+ex,n[1]),(x+ex,p[3])],
                    [(x,p[3]),(x,p[4])] ]
        else:
            lines = [ [(x,p[0]),(x,p[1])],
                    [(x+ex,p[1]),(x+ex,p[2]-ey)],
                    [(x+ex,p[2]+ey),(x+ex,p[3])],
                    [(x,p[3]),(x,p[4])] ]
        lines = pl.array(lines)
        if self.vert==1:
            lines = pl.array([ pl.c_[l[:,1],l[:,0]] for l in lines ])
            pt = self.axes.plot ( f_lo, [x]*len(f_lo), '.', color=self.color,
                    markersize=self.lw ) + \
                self.axes.plot ( f_hi, [x]*len(f_hi), '.', color=self.color,
                    markersize=self.lw )
            dummy = self.axes.plot ( [p[0],p[-1]],[x-ex,x+ex], '.', markersize=0 )
        else:
            pt = self.axes.plot ( [x]*len(f_lo), f_lo, '.', color=self.color,
                    markersize=1 ) + \
                self.axes.plot ( [x]*len(f_hi), f_hi, '.', color=self.color,
                    markersize=1 )
            dummy = self.axes.plot ( [x-ex,x+ex], [p[0],p[-1]], '.', markersize=0 )
        box = LineCollection (
                segments=lines,
                linewidths=[self.lw]*lines.shape[0],
                colors=[self.color]*lines.shape[0] )
        box.set_transform ( self.axes.transData )
        box.set_zorder(10)
        return box, pt[0],dummy[0]


class RangeFrameArtist (Artist):
    def __init__ ( self, x, y, trim=False ):
        Artist.__init__(self)
        self.x = x
        self.y = y
        self.trim = trim

    def draw ( self, renderer, *args, **kwargs ):
        if not self.get_visible(): return

        rf = self.make_range_frame()
        rf.draw(renderer)

    def make_range_frame (self):

        rx = self.axes.get_xlim()
        ry = self.axes.get_ylim()
        px = pl.prctile ( self.x )
        py = pl.prctile ( self.y )

        if self.trim:
            if px[2]-px[0]>1.5*(px[3]-px[1]):
                px[0] = self.x[self.x>px[2]-1.5*(px[3]-px[1])].min()
            if px[4]-px[2]>1.5*(px[3]-px[1]):
                px[4] = self.x[self.x<px[2]+1.5*(px[3]-px[1])].min()

        x = px-rx[0]
        x /= rx[1]-rx[0]
        y = py-ry[0]
        y /= ry[1]-ry[0]
        ex = .003
        ey = .003
        xline = [
                [(x[0],0),(x[1],0)],
                [(x[1],ey),(x[2]-ex,ey)],
                [(x[2]+ex,ey),(x[3],ey)],
                [(x[3],0),(x[4],0)]
                ]
        yline = [
                [(0,y[0]),(0,y[1])],
                [(ex,y[1]),(ex,y[2]-ey)],
                [(ex,y[2]+ey),(ex,y[3])],
                [(0,y[3]),(0,y[4])]
                ]
        widths = [1,1,1,1]
        range_lines = LineCollection(
                segments=pl.clip(xline+yline,0,1),
                linewidths=widths+widths,
                colors=[[0]*3]*2*len(widths) )
        range_lines.set_transform ( self.axes.transAxes )
        range_lines.set_zorder(10)

        self.axes.get_xaxis().tick_bottom()
        self.axes.get_yaxis().tick_left()
        self.axes.set_xticks(px)
        self.axes.set_yticks(py)
        self.axes.tick_params ( width=0 )

        return range_lines
