dvis
====

customized matplotlib extensions

I have a number of standard matplotlib "hacks", that I keep reinventing over
and over. This "project" is an effort to do these things once -- and
well. The "hacks" that are collected in this repository all build on
matplotlib and are meant to improve on its features for **d** ata
**vis** ualization.

Installation
------------

dvis obviously depends on `matplotlib <http://http://matplotlib.org/>`_.

To install dvis, simply download the sourcecode and type

sudo python setup.py install

After that, you should be able to use dvis.

Using dvis
----------

To start using dvis, simply import dvis in python, along with matplotlib. You
could for example do::

    >>> import pylab as pl
    >>> import dvis

And you have the functions from dvis available. Dvis is not meant to provide a
complete plotting environment -- matplotlib is so much better at this -- but it
provides some things that are meant to simplify things that I often find
complicated with matplotlib, or that I often do in multilinestatements. Here
are some examples:

Mixing colors
.............

You would like to use color to mark different conditions in your paper, but you
would like to have these conditions to distinct when your paper is printed on a
black-and-white printer? `Vinzenz Schönfelder
<http://www.cognition.tu-berlin.de/menue/members/vinzenz_schoenfelder/>`_
provided me with some nice color schemes that print well in black and white as
well as in color. They are in the color module, or in the main workspace and
they come in a three color version and a four color version::

    >>> dvis.col3
    [(0.09803921568627451, 0.09803921568627451, 0.4392156862745098), (1.0, 0.27058823529411763, 0.0), (0.7843137254901961, 1.0, 1.0)]
    >>> dvis.col4
    [(0.09803921568627451, 0.09803921568627451, 0.4392156862745098), (0.13333333333333333, 0.5450980392156862, 0.13333333333333333), (1.0, 0.8431372549019608, 0.0), (0.9411764705882353, 1.0, 1.0)]

Now, you might feel that the last color in col4 is a bit too bright and you
might want to mix in some black. You can use::

    >>> dvis.cmix(dvis.col4[-1],'black',4)
    [0.7529411764705882, 0.8, 0.8]

Here, the last number means that the ratio of dvis.col4[-1] to black is 4, i.e.
there is four times as much dvis.col4[-1] in the result as there is black.

Reworked data displays
......................

I like `Ed Tufte's <http://www.edwardtufte.com/tufte/>`_ ideas about data
display. In particular, I like his reworked boxplot and the associated scatter
plot. The boxplot is just a very reduced version: The "box" is just marked by a
small offset in a vertical line and the marker for the median is a small gap in
this vertical line. The idea of the revised scatter plot is to replace the axes
by these boxplot "lines"::

    >>> x,y = pl.randn ( 2,100 )
    >>> dvis.Boxplot ( pl.c_[x,y] )
    >>> dvis.Scatter ( x, y ) # doctest: +ELLIPSIS
    <matplotlib.collections.PathCollection object at ...>

In addition, I occasionally want to plot curves with an estimation error. To
show these, I like to have something like an error region around these curves.
So these are not really error bars, but rather a complete region of errors. The
Errorline does exactly that::

    >>> x = pl.mgrid[0:10:100j]
    >>> y = (x-3)**2 + 2
    >>> error = .01*y
    >>> dvis.Errorline ( x, y, error ) # doctest: +ELLIPSIS
    ([<matplotlib.lines.Line2D object at ...>], [<matplotlib.patches.Polygon object at ...>])

Here, the first return element is the actual line, the second is the filled
error region.

Placing and customizing axes
............................

There are two things I don't like about matplotlib: 1. Frames around a plot are
ugly. 2. placing axes using subplot is very inflexible. There are ways around
that in matplotlib, namely spines (for 1) and axes_grids (for 2).
Unfortunately, both are hidden fairly deep in the matplotlib code and need to
be tweaked manually. There are two functions that do the manual tweaking as
automatical as possible. Yet, in order to use them, you should probably know a
bit about how things would be done in matplotlib

    >>> dvis.prepare_axes ( pl.axes() ) # doctest: +ELLIPSIS
    <matplotlib.axes.AxesSubplot object at ...>
    >>> dvis.axes_grid ( (3,2) )
    array([[Axes(0.05,0.05;0.9x0.9), Axes(0.05,0.05;0.9x0.9)],
           [Axes(0.05,0.05;0.9x0.9), Axes(0.05,0.05;0.9x0.9)],
           [Axes(0.05,0.05;0.9x0.9), Axes(0.05,0.05;0.9x0.9)]], dtype=object)


