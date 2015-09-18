#!/usr/bin/env python

# vim: set noexpandtab ts=8:

#this program generates random coordinations and orientations (for spherocylinders) in chains of size N



import os
import sys
import math
import optparse
import commands
import string
import random
import gzip
import usefulmath


def gennewcoord(pbc):
    #generate random vector on 1 sphere
    orient=usefulmath.vec_random()
    orient=usefulmath.vec_normalize(orient)

    #generate position
    pos=[random.random()*float(pbc[0]),random.random()*float(pbc[1]),random.random()*float(pbc[2])]
    
    #generate patch (perpendicular to orientation of cylinder)
    patch=usefulmath.perp_vec(orient)
    patch=usefulmath.vec_normalize(patch)
    
    #return [pos,orient]
    return [pos,orient,patch]

def make(numsc,numch,pbc):
    data=[]
    ## step size is basicly lenghth of sc ... length by which sc is shifted
    step_size=4.2
    #print numsc,numch,pbc,output_path

    for i in xrange(int(numch)):
        data.append(gennewcoord(pbc))
    ##data in form [sc, sc, ..] sc=[[center],[orientation],[patch orientation]]
    #print data

    new_data=[]
    for i in range(int(numch)):
        for t in range(int(numsc)):
            #print "\n\n\n",t
            #print [data[i][0][x]+data[i][1][x]*step_size*t for x in xrange(3)]
            #print "\n\n\n"            
            new_data.append([[data[i][0][x]+data[i][1][x]*step_size*t for x in xrange(3)],data[i][1],data[i][2]])
    
    outstring=""
    for i in xrange(len(new_data)):
        for part in new_data[i]:
            for piece in part:
                outstring+=str(piece)+" "
	if i < len(new_data)-1:
	    outstring+=" 0 0\n"
    outstring+=" 0 0"

    boxsize = ""
    for i in pbc:
        boxsize+=i+" "
    print boxsize
    print outstring

    return 0

parser=optparse.OptionParser()
help="""Usage:
%program [options] 
pbc is set as string ("100 15 24")
"""
parser.set_usage(help)
parser.add_option(
    "-c",
    "--chainsnum",
    help="Number of chains",
    dest="chnum"
    )
parser.add_option(
    "-n",
    "--scnum",
    help="Number of cylinders in chain",
    dest="scnum",
    default="1"
    )
parser.add_option(
    "--pbc",
    help="Set size of box you want to use \"x y z\"]",
    dest="pbc"
    )

(options,arguments)=parser.parse_args()
if not options.pbc:
    sys.exit("Error: You have to set size of box (--pbc)")
make(options.scnum,options.chnum,options.pbc.split())
