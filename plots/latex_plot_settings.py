import math
from matplotlib import rcParams


def configure(document_fontsize=11.0, available_width=336.0):
    """
    Configures Matplotlib so saved figures can be used in LaTeX documents.
    Uses the sans-serif TeX Gyre Heros font (Helvetica), also for math.
    Arguments:
    - document_fontsize: Font size in points (use "\the\fontdimen6\font" in
      your LaTeX document to get the current value). The default is for a
      LaTeX Beamer document at 14pt ("\documentclass[14pt]{beamer}") which
      for some reason is slightly more than 14pt.
    - available_width: The available width in your LaTeX document, usually
      the value of "\textwidth". The default is for a LaTeX Beamer document
      with the default theme.
    Returns a function that calculates figure size given a fraction of the
    available width for the figure to occupy.
    Figures can be saved as PDF:
        fig.tight_layout(pad=0.1)
        fig.savefig('figure.pdf')
    And included in your document as follows:
        \begin{frame}
          \begin{center}
            \includegraphics[width=1.0\textwidth,transparent]{figure.pdf}
          \end{center}
        \end{frame}
    Todo:
    - Make font family and face configurable.
    - Example IPython Notebook and LaTeX document.
    - Document dependencies (tex-gyre, dvipng, ...).
    Based on: http://damon-is-a-geek.com/publication-ready-the-first-time-beautiful-reproducible-plots-with-matplotlib.html
    """
    def figsize(width_fraction=1.0):
        """
        width_fraction: The fraction of the available width you'd like the figure to occupy.
        """
        width_pt = available_width * width_fraction

        inches_per_pt = 1.0 / 72.27
        golden_ratio  = (math.sqrt(5) - 1.0) / 2.0

        width_in = width_pt * inches_per_pt
        height_in = width_in * golden_ratio
        return width_in, height_in

    rcParams['font.size'] = document_fontsize
    rcParams['axes.titlesize'] = document_fontsize
    rcParams['axes.labelsize'] = document_fontsize
    rcParams['xtick.labelsize'] = document_fontsize
    rcParams['ytick.labelsize'] = document_fontsize
    rcParams['legend.fontsize'] = document_fontsize
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['tgheros']
    rcParams['font.serif'] = ['cm10']
    rcParams['text.usetex'] = True
    rcParams['text.latex.preamble'] = r"""
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{tgheros}
\usepackage[tx]{sfmath}
"""
    rcParams['figure.figsize'] = figsize()

    return figsize
