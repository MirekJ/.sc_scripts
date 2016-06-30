#!/usr/bin/env python

#this program generates random coordinations and orientations (for spherocylinders) in chains of size N

CUT_OFF=0.001
PI=3.1415926535897932384626433832795028841971693993751058209749
SIGMA=1.2
SIM_TO_REAL_TRANSITION_LENGHTH=7.12719167
LENGHT=3
# funguje spravne jen tehdy kdyz maj vsechny castice stejnou delku !!!!
P_PER_CUBIC_ANGSTROM_WATER=0.0332575


import os
import sys
import math
import optparse
import commands
import string
import random
import gzip
import usefulmath


def gennewcoord(pbc,dist):
    #generate random vector on 1 sphere
    orient=usefulmath.vec_random()
    orient=usefulmath.vec_normalize(orient)

    dist=float(dist);
    dist2=2.0*dist;

    #generate position
    pos=[dist+random.random()*(float(pbc[0])-dist2),dist+random.random()*(float(pbc[1])-dist2),dist+random.random()*(float(pbc[2])-dist2)]
    
    #generate patch (perpendicular to orientation of cylinder)
    patch=usefulmath.perp_vec(orient)
    patch=usefulmath.vec_normalize(patch)
    
    #return [pos,orient]
    return [pos,orient,patch]

def make(numsc,dist,numch,pbc,output_path):
    volume=1.0
    for i in pbc:
        volume=volume*float(i)
    number_of_particles=float(numsc)*float(numch)
    particle_volume=(PI*SIGMA*SIGMA*(0.25*LENGHT+(1/6)*SIGMA))*number_of_particles
    water_volume=volume-particle_volume
    number_of_water=water_volume*(SIM_TO_REAL_TRANSITION_LENGHTH**3)*P_PER_CUBIC_ANGSTROM_WATER
    num_of_all_molecules=number_of_particles+number_of_water
    volume_fraction=particle_volume/volume

    if output_path:
        print "Volume:\t\t\t"+str(volume)
        print "Volume of particles:\t"+str(particle_volume) 
        print "Volume of water:\t"+str(water_volume)
        print "Volume fraction:\t"+str(volume_fraction)

    data=[]
    ## step size is basicly lenghth of sc ... length by which sc is shifted
    step_size=4
    #print numsc,numch,pbc,output_path

    for i in xrange(int(numch)):
        data.append(gennewcoord(pbc,dist))
    ##data in form [sc, sc, ..] sc=[[center],[orientation],[patch orientation]]
    #print data

    new_data=[]
    for i in range(int(numch)):
        for t in range(int(numsc)):
            #print "\n\n\n",t
            #print [data[i][0][x]+data[i][1][x]*step_size*t for x in xrange(3)]
            #print "\n\n\n"            
            new_data.append([[data[i][0][x]-data[i][1][x]*step_size*t for x in xrange(3)],data[i][1],data[i][2]])
    
    outstring=""
    for sc in new_data:
        for part in sc:
            for piece in part:
                outstring+=str(piece)+" "
        outstring+=" 0\n"
    #print outstring

    if output_path:
        output_file = open(output_path, 'w')
        boxsize = ""
        for i in pbc:
            boxsize+=i+" "
        boxsize+="\n"
        output_file.write(boxsize)
        try:
            output_file.write(outstring)
        finally:
            output_file.close()
    else:
        print outstring[:-1]
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
    "-d",
    "--distance",
    help="Distance from box sides",
    dest="dist",
    default="0"
    )
parser.add_option(
    "-o",
    "--output",
    help="Set to which file you want to save data",
    dest="outfilename"
    )
parser.add_option(
    "--pbc",
    help="Set size of box you want to use \"x y z\"]",
    dest="pbc"
    )


(options,arguments)=parser.parse_args()
if not options.pbc:
    sys.exit("Error: You have to set size of box (--pbc)")
make(options.scnum,options.dist,options.chnum,options.pbc.split(),options.outfilename)



