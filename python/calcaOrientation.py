#!/usr/bin/python
import optparse
import sys
import math
import numpy as np


class vec(object):
    def __init__(self, *args):
        self.__values = []
        if args:
            if(len(args) == 1): ## Only one argument were provided
                if(type(args[0]) == list):
                    for value in args[0]:
                        try:
                            self.__values.append(float(value));
                        except:
                            raise Exception("Wrong format of arguments provided for vector construction!")
                else:
                    raise Exception("Only one argument for vector constructor were specified and it wasnt a list!")
            else: ## more arguments were specified lets fill the vector with them
                for value in args:
                    try:
                        self.__values.append(float(value));
                    except:
                        raise Exception("Wrong format of arguments provided for vector construction!")
        else:
            raise Exception("No arguments to vector constructor were supplied!")
        self.size = len(self.__values)
### ------ INIT END ----- ###

    def __str__(self):
        output = "["
        for value in self.__values:
            output+=str(value)+","
        output=output[:-1]+"]"
        return output

    def __add__(self, other):
        if(not issubclass(other.__class__, vec)):
            raise Exception("Argument is not a vector!")
        if(self.size == other.size):
            res = []
            for i in xrange(self.size):
                res.append(self.__values[i]+other._vec__values[i])
            return vec(res)
        else:
            raise Exception("You cant add vectors of different size!")

    def __sub__(self, other):
        if(not issubclass(other.__class__, vec)):
            raise Exception("Argument is not a vector!")
        if(self.size == other.size):
            res = []
            for i in xrange(self.size):
                res.append(self.__values[i]-other._vec__values[i])
            return vec(res)
        else:
            raise Exception("You cant add vectors of different size!")


    def __iadd__(self, other):
        if(not issubclass(other.__class__, vec)):
            raise Exception("Argument is not a vector!")
        if(self.size == other.size):
            for i in xrange(self.size):
                self.__values[i]+=other._vec__values[i]
            return self
        else:
            raise Exception("You cant add vectors of different size!")

    def __isub__(self, other):
        if(not issubclass(other.__class__, vec)):
            raise Exception("Argument is not a vector!")
        if(self.size == other.size):
            for i in xrange(self.size):
                self.__values[i]-=other._vec__values[i]
            return self
        else:
            raise Exception("You cant add vectors of different size!")        

    def norm(self):
        ## Return length of vector
        suma=0.0
        for value in self.__values:
            suma+=value*value;
        return math.sqrt(suma)

    def ScalarProduct(self, other):
        res=0.0
        for i in xrange(self.size):
            res+=self.__values[i]*other._vec__values[i]
        return res

    def __mul__(self, other):
        if(issubclass(other.__class__, vec)):
            return self.ScalarProduct(other)
        try:
            multiplicator = float(other)
        except:
            raise Exception("Not supported multiplication!")
        res=[]
        for i in xrange(self.size):
            res.append(self.__values[i]*multiplicator)
        return vec(res)
        
    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        if(issubclass(other.__class__, vec)):
            raise Exception("You cant divide vector by vector!")
        try:
            divider = float(other)
        except:
            raise Exception("Not supported multiplication!")
        res=[]
        for i in xrange(self.size):
            res.append(self.__values[i]/divider)
        return vec(res)

    def __rdiv__(self, other):
        raise Exception("You cant use vector as denominator!")

    def __getitem__(self, index):
        if(type(index) == int):
            return self.__values[index]
        else:
            raise Exception("To acces vector values with index, index must be of type int!")

    def __setitem__(self, key, value):
        self.__values[key]=value
        
    def __iter__(self):
        return iter(self.__values)

      
    def Angle(self, other):
        if(other.size != self.size):
            raise Exception("Wrong dimension or type of vector!")
        res=self*other/(math.sqrt(other * other)*math.sqrt(self*self))
        return math.acos(res)
  

class vec3(vec):
    def __init__(self, *args):
        vec.__init__(self, *args)
        if(self.size != 3):
            raise Exception("Wrong number of arguments for vector of size 3!")

    @property
    def x(self):
        return self._vec__values[0]
    @x.setter
    def x(self, value):
        self._vec__values[0] = value

    @property
    def y(self):
        return self._vec__values[1]
    @y.setter
    def y(self, value):
        self._vec__values[1] = value

    @property
    def z(self):
        return self._vec__values[2]
    @z.setter
    def z(self, value):
        self._vec__values[2] = value

    def QuatRot(self, axis, angle):
        quat=[math.cos(angle/360.0*math.pi),\
              axis.x*math.sin(angle/360.0*math.pi),\
              axis.y*math.sin(angle/360.0*math.pi),\
              axis.z*math.sin(angle/360.0*math.pi)]
        t2  =  quat[0] * quat[1]
        t3  =  quat[0] * quat[2]
        t4  =  quat[0] * quat[3]
        t5  = -quat[1] * quat[1]
        t6  =  quat[1] * quat[2]
        t7  =  quat[1] * quat[3]
        t8  = -quat[2] * quat[2]
        t9  =  quat[2] * quat[3]
        t10 = -quat[3] * quat[3]
        newx = 2.0 * ( (t8+t10)*self.x +  (t6-t4)*self.y + (t3+t7)*self.z ) + self.x
        newy = 2.0 * (  (t4+t6)*self.x + (t5+t10)*self.y + (t9-t2)*self.z ) + self.y
        newz = 2.0 * (  (t7-t3)*self.x +  (t2+t9)*self.y + (t5+t8)*self.z ) + self.z
        self.x = newx
        self.y = newy
        self.z = newz

        


class ParticleConf(object):
    def __init__(self, position=None, direction=None, patch=None, switchType=None, molType=None):
        if( (position is None) and (direction is None) and (patch is None)\
            and (switchType is None) and (molType is None)):
            ## Initialization without parameters ... new particle
            self.__SETPOS([0.0, 0.0, 0.0])
            self.__SETDIR([0.0, 0.0, 0.0])
            self.__SETPAT([0.0, 0.0, 0.0])
            self.__SETSWT(0)
            self.__SETMOT(0)
        elif(type(position) == str):
            ## Initialize particle from string
            self.ReadString(position)
        elif( (position is not None) and (direction is not None) and (patch is not None)\
            and (switchType is not None) and (molType is not None)):
            ## Initialize particle by properties
            self.__SETPOS(position)
            self.__SETDIR(direction)
            self.__SETPAT(patch)
            self.__SETSWT(switchType)
            self.__SETMOT(molType)
        else:
            raise Exception("Wrong parameters for ParticleConf __init__!")

    def __SETPOS(self, position):
        self.pos = vec3(position)

    def __SETDIR(self, direction):
        self.dir = vec3(direction)

    def __SETPAT(self, patch):
        self.pat = vec3(patch)

    def __SETSWT(self, switchType):
        try:
            self.swt = int(switchType)
        except:
            raise Exception("Switch type is not a number!")

    def __SETMOT(self, molType):
        try:
            self.mol = int(molType)
        except:
            raise Exception("Mol type is not a number!")        

    def __str__(self):
        return "%15.8e %15.8e %15.8e\t\t%15.8e %15.8e %15.8e\t\t%15.8e %15.8e %15.8e\t\t%i %i" \
               % (self.pos[0], self.pos[1], self.pos[2],\
                  self.dir[0], self.dir[1], self.dir[2],\
                  self.pat[0], self.pat[1], self.pat[2],\
                  self.swt, self.mol)
    def Dir(self):
        return self.dir

    def Translate(self, other):
        if(not issubclass(other.__class__, vec)):
            raise Exception("Translatin must be a vector!")
        else:
##            print >> sys.stderr, "before"+str(self)
            self.pos+=other
##            print >> sys.stderr, "after"+str(self)

    def UsePBC(self, box):
        box_iter=iter(box);
        for i in xrange(3):
            box_size=box_iter.next();
            if(self.pos[i] < 0):
                self.pos[i]+=box_size;
            elif(self.pos[i] > box_size):
                self.pos[i]-=box_size;

    def ReadString(self, string):
        splits=string.split()
        if(len(splits) == 10):## Because of consistency with old sc35 version
            self.__SETPOS(splits[0:3])
            self.__SETDIR(splits[3:6])
            self.__SETPAT(splits[6:9])
            self.__SETSWT(splits[9])
            self.__SETMOT(0)
        elif(len(splits) == 11):
            self.__SETPOS(splits[0:3])
            self.__SETDIR(splits[3:6])
            self.__SETPAT(splits[6:9])
            self.__SETSWT(splits[9])
            self.__SETMOT(splits[10])
        else:
            raise Exception("Movie file data doesnot fit format !")

def calcOri(inputPath):
    movieFile = open(inputPath,'r')
    dirSum=vec3(0,0,0);
    num=0.0;
    for line in movieFile:
        splits = line.split()
        if ( len(splits)>=10 ):
            dirSum+=ParticleConf(line).Dir();
            num+=1.0;

    print dirSum*(1.0/num);
    return
    
parser=optparse.OptionParser(epilog="Script calculate mean orieantation vector and its magnitude.")
parser.set_usage(usage="""%prog [option1] <arg1> [option2] <arg2> ....
""")
parser.add_option(
    "-i",
    "--input",
    help="Movi file",
    dest="input"
    )

(options,arguments)=parser.parse_args()
if not options.input:
    sys.exit("Error: You have to set input file\nFor help type in argument -h or --help")
calcOri(options.input)


