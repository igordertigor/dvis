Writing structured code to produce publication figures
======================================================

For a bit, I've been thinking how to write readable code to produce figures for
publications. I create my figures with matplotlib, which provides good
input-output functionality and can pretty much produce any type of plot that
you might want. Some people swear on other things, most notably probably
ggplot2, but matplotlib has served me well over the years and I'm just most
familiar with python.

The problem with writing scripts to generate figures is that very often (and
also in matplotlib) the default settings of the packages are pretty far from
what you would like your figure to look like. In writing this tutorial, I will
try to summarize some points that helped me focus on the figure rather than
find the line where that one setting was made.


Create a folder structure
-------------------------

This is the first step. You want every figure to have its own script that
generates it. In addition, you want one folder for the final figures and one
file for global settings. In some cases, you also need a file to load the data
you want to plot. So lets assume, you know what figures you want and you need a
file to load the data. Then your whole directory would look like this::

    $ ls
    figures/        figure1.py      figure2.py
    figure3.py      loading.py      settings.py

Of course, with more figures, you need the respective additional files.


Use rcParams
------------

Matplotlib changes the overall defaults for a lot of graphics parameters
through a dictionary called rcParams. In an interactive python session, you can
type::

    rcParams.keys()

To see a list of all the things that can be set. Typically, journals require
certain fontsizes and give you which ones they want. You can open your
settings.py and set them there::

    import pylab as pl

    rcParams['xtick.labelsize'] = 8
    rcParams['ytick.labelsize'] = 8
    rcParams['axes.titlesize'] = 12
    rcParams['axes.labelsize'] = 10
    rcParams['font.size'] = 10

There are tons of other things that can be set in rcParams. Some of them will be useful, while others might not be relevant for you or might just be at really sensible settings already.


Create condition colors
-----------------------

In most cases, you will want to plot data from different conditions and the text that you write will mostly be about the fact that these conditions differ in something or are the same in something else. For example, you might want to explain how your theory (condition) resembles the data from an experiment (condition) or how a measured profile measured on one day (condition) differs from the profile on another day (condition). I find it helpful to define the colors centrally in the settings file and then use meaningful names when I actually create the figures. That is I add to the settings file something like::

    colors = {
        'theory':   '#006600',
        'experiment': '#0000ff'
    }

I find it helpful to use one of the online color pickers for web designers to choose nice colors for the plot (for example `this one <http://www.w3schools.com/tags/ref_colorpicker.asp>`_). For some journals, you can't use color but have to vary linestyle or grayscale. I guess it is clear how to structure that.


Use keyword expansion
---------------------

Keyword expansion is a powerful python mechanism. For those who forgot it, here is how it works::

    >> def testfunction(*args, **kwargs):
    ..     print "I received the following positional arguments", args
    ..     print "I received arguments for the following keywords"
    ..     for kw, arg in kwargs.iteritems():
    ..         print kw, "=", arg
    >> testfunction(1, 2, 4, dust='sand', foo='bar)
    I received the following positional arguments (1, 2, 3)
    I received arguments for the following keywords
    dust = sand
    foo = bar

Thus, in testfunction, the positional arguments are represented as a tuple and the keyword arguments are assembled as a dictionary. Now the really nice thing is that *instead of writing out the list of keyword arguments, we can just pass the dictionary*::

    >> kwargs = {'dust': 'sand', 'foo': 'bar}
    >> testfunction(**kwargs)
    I received the following positional arguments ()
    I received arguments for the following keywords
    dust = sand
    foo = bar

We can use this mechanism to store groups of keyword arguments that we will often use together. For example, we might want to have some special settings for the title of a figure (rcParams somehow doesn't seem to support this)::

    titleparams = {
        'horizontalalignment': 'left',
        'verticalalignment': 'bottom',
        'loc': 'left'
    }

This will give a left aligned title over the left side of the figure or subplot. Useful if you label your subplots by A), B), ... In your figure script you would then just call::

    import settings as st

    # Now a bunch of stuff that actually creates a meaningful figure
    # ...

    # Now set the title
    pl.title('A)', **st.titleparams)

If you always use this mechanism, all your titles will be created in the same way. It is of course, easy to define similar dictionaries to store line properties or other settings.


Use one file per figure and make
--------------------------------

As you have seen above, I used one file per figure. This helps to keep track of what's happening in that figure. You shouldn't do any analysis in the figure scripts anymore, so there should be no need to keep data from one figure to the next. Store relevant data and intermediate results in files and just load what you need. The advantage of having one file per figure is that you can have a makefile to specify how the figures are generated. For example::

    figures/fig1.pdf: figure1.py settings.py
        python figure1.py

In the Makefile specifies that figures/fig1.pdf depends on (i) figure1.py and (ii) settings.py. If you type make on the commandline, make will first check if either figure1.py or settings.py have changed. If they haven't, then obviously figures/fig1.pdf can't have changed and nothing needs to be done. If however, either figure1.py or settings.py have changed, make will run the command::

    python figure1.py

To update (or create) figures/fig1.pdf. Make will always just make sure that the first entry in the makefile is up to date. However, this first entry can just be a keyword, in which case it is never up to date. You can use that with more than one figure in the following way::

    allfigures: figures/fig1.pdf figures/fig2.pdf

    figures/fig1.pdf: figure1.py settings.py
        python figure1.py

    figures/fig2.pdf: figure2.py settings.py
        python figure2.py

Thus, whenever you call make, the program will first check if allfigures is up to date. Because it is a keyword, it will never be up to date. Make will then check if the things that allfigures depends on are up to date and run the associated commands if necessary. Because allfigures depends on all the figures that we want to keep up to date, this ensures that by calling make, all figures will actually be updated as necessary.


Good figure sizes
-----------------

Most journals have recommendations as to how wide a figure with one column and one with two columns should be. You can have those sizes in your settings.py and then just create a one columns figure by::

    pl.figure(figsize=(st.onecol, 3))

and similar for a two column figure.


Add a figure saver
------------------

Depending on the journal, you will need different types of graphics files. Most journals will like eps and or tiff, while you might want something smaller (for example pdf and png) for proofreading. Also, pdflatex does not support eps, so that it often helps to have a pdf version of vector figures. For some cases, you also might want svg figures. It is helpful, to think about (i) which figure format you definitely need and (ii) which secondary figure formats would be useful. For example, I find that I definitely want my figures as pdfs, but that I also often want them as eps. That's why my Makefile (see above) expresses the dependencies for pdfs. In addition, I have a function in my settings file that manages saving of figures in the following way::

    def savefigure(name):
        pl.savefig('figures/%s.pdf' % (name,))
        pl.savefig('figures/%s.eps' % (name,))
        pl.savefig('figures/%s.png' % (name,))

I use this figure to actually store my figures. The advantage of this is, that whenever I realize that I need my figures in an additional format (for example tiff), I can just modify this one savefigure file and type make.


Good looks
----------

Creating pretty figures, needs some practice. Typically, I feel that Tufte's recommendation to "maximize data ink" is helpful, but doesn't do all. For example, minimizing label ink, can easily lead to unreadable labels, which doesn't help understanding the data you show. I've tried to combine some things that I often use in `dvis <https://github.com/igordertigor/dvis>`_. I don't use all of them anymore, but the colors (col3 and col4) are nice, because they are easy to discriminate in color and grayscale. I also often use the command prepare_axes, which essentially handels matplotlib's spine functionality. When using that, I often observed that it wasn't particularly easy to put plots in the right places so that the labels don't overlap and the plot area is efficiently used. For nearly all plots, it turns out that you can fix this by calling::

    pl.tight_layout()

at the end of your script (or before you save the figure).


Multiple axes
-------------

Multiple axes are handeld by the subplot function. Unfortunately, this function is limited when it comes to more complex layouts or when you want more then 9 subplots (subplot(559) will give you plot the 4th plot in the second row of a grid of 5x5 subplots, while 5510 will generate an error). I found that matplotlib.gridspec helps with that (and is compatible with tight_layout). Also, mpl_toolkits.axes_grid1 contains a number of helpful tools to position axes relative to each others with little code. Take a look at their documentation if you have to deal with multiple axes setups that subplot doesn't quite handle.
