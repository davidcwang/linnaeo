# LINNAEO #

Linnaeo is a python program I made mostly as an exercise in learning how to code GUI programs... but also to solve a 
basic problem I had: nothing out there is very good for storing and making protein alignments.


### Protein alignments? ###

Yes, out there in the world are countless amino acid sequences, and their sequences are connected to
protein functions... but it's often hard to see that. This program is intended to help with this 
by meeting a few basic criteria:

1) It should be fast.
2) It should store any sequence you want.
3) It should be easy to create and store alignments. 

That's a basic idea. Most likely those criteria will change. 

### How do I get set up? ###

I am going to try and make this into a package that installs automagically, but for now 
here is a list of the packages I installed into a fresh python environment:

* Python v3.8
* PyQt5
* biopython
* A port of Clustal Omega (in this repository)
* PyQt5-stubs==5.14.2.0 (for code hints)

I'm trying to get this into a conda package that can be installed easily (akin to PyMOL -- they figured it out somehow!). Here's hoping I am successful. If I am, I'll be sure to update that here.

Repositories I am eternal grateful for and need to cite: 

* [ARGTABLE2](https://github.com/jonathanmarvens/argtable2) -- for building Clustal Omega on Windows
* [Clustal Omega, adapted to use CMake (SO, SO GRATEFUL) from GSL Biotech (You guys rock, seriously)](https://github.com/GSLBiotech/clustal-omega/tree/master/src)
* 
