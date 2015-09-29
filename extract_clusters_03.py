#!/usr/bin/env python
# vim: set noexpandtab ts=4:


import optparse
import math
import sys
import copy

ANGLE_TOLERANCE=20.0
PATCH_ANGLE_TOLERANCE=10.0
TCPSC_ANGLE=40.0
DISTANCE_FROM_COM_TOLERANCE=0.5
CLUSTER_ENERGY=-3.5
CLUSTER_ENERGY_TOLERANCE=555550.5


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

class ParticleCluster(object):
    ##TODO: center cluster .. translate cluster so that first particle is in cnter of box(so even particles on boundery are transformed right), then usePBC, then calc COM, then translate COM to center of box
    def __init__(self):
        self.__particleList = []
        self.energy         = 0.0
        self.size           = 0
        self.mass           = 0.0
        self.com            = vec3(0.0,0.0,0.0)
        

    ## Data structure is    clusterList = [ particle, particle, particle ]
    ##                      particle    = [ParticleConf, mass, ...]

    def __CENTEROFMASS(self):
        mass_of_cluster = 0.0
        center_of_mass  = vec3(0.0,0.0,0.0)
        for particle in self.__particleList:
            center_of_mass+=particle[0].pos*particle[1]
            mass_of_cluster+=particle[1]
        self.mass  = mass_of_cluster
        self.com   = center_of_mass/mass_of_cluster

    def UsePBC(self,box):
        for particle in self.__particleList:
            particle[0].UsePBC(box)
        self.__CENTEROFMASS()

    def append(self, particle, mass):
        if(issubclass(particle.__class__, ParticleConf)):
            self.__particleList.append([particle, mass]);
            self.size+=1;
            self.__CENTEROFMASS()
        else:
            raise Exception("Only ParticleConf objects can be added into cluster!")

    def MovieFrame(self, sweep, box):
        movie = MovieFrame(sweep, box)
        for particle in self.__particleList:
            movie.append(particle[0])
        return movie

    def __MEANDISTANCEFROMCOM(self):
        dist = 0.0
        for particle in self.__particleList:
            dist+=(particle[0].pos-self.com).norm()
        return dist/self.size

##    def arePatchsPointingToCOM(self, tolerance):
##        ## Lets make sum of patch vector distances from COM, if all patches point to center of cluster SUM is close to zero
##        distance_sum = 0.0
##        for particle in self.__particleList:
##            particle_distance_to_COM = (particle[0].pos-self.cmass).norm()
##            distance_sum+=((particle[0].dir*particle_distance_to_COM)-self.com).norm()
##        if((distance_sum/self.size) > tolerance):
##            return False
##        else:
##            return True

    def arePatchsPointingToCOM_TCPSC(self, tolerance, box, rot):
        ## Lets make sum of patch vector distances from COM, if all patches point to center of cluster SUM is close to zero
        if(self.size <= 1):
            return True
        box=[float(i) for i in box]
        self.UsePBC(box)
        angle_distance_sum = 0.0
        for particle in self.__particleList:
            vector_to_COM = self.com-particle[0].pos
            path_vec=copy.deepcopy(particle[0].pat)
            path_vec.QuatRot(particle[0].dir, rot)
##            print "COM", self.com
##            print "POS", particle[0].pos
##            print "res", vector_to_COM
##            print "pat", particle[0].pat
##            print "scalar", sum([vector_to_COM._vec__values[i]*particle[0].pat._vec__values[i] for i in xrange(3)])
##            print "norm COM", vector_to_COM.norm()
##            print "norm pat", particle[0].pat.norm()
            angle=math.fabs(math.degrees(path_vec.Angle(vector_to_COM)))
##            print "angle", angle
            angle_distance_sum+=min(angle, (-1.0*(angle-180.0)))
##            print angle,(-1.0*(angle-180.0)), min(angle, (-1.0*(angle-180.0)))
##        print angle_distance_sum
        if((angle_distance_sum/self.size) > tolerance):
            return False
        else:
            return True



    def arePatchsPointingToCOM2(self, tolerance, box):
        ## Lets make sum of patch vector distances from COM, if all patches point to center of cluster SUM is close to zero
        if(self.size <= 1):
            return True
        box=[float(i) for i in box]
        self.UsePBC(box)
        angle_distance_sum = 0.0
        for particle in self.__particleList:
            vector_to_COM = self.com-particle[0].pos
##            print "COM", self.com
##            print "POS", particle[0].pos
##            print "res", vector_to_COM
##            print "pat", particle[0].pat
##            print "scalar", sum([vector_to_COM._vec__values[i]*particle[0].pat._vec__values[i] for i in xrange(3)])
##            print "norm COM", vector_to_COM.norm()
##            print "norm pat", particle[0].pat.norm()
            angle=math.fabs(math.degrees(particle[0].pat.Angle(vector_to_COM)))
##            print "angle", angle
            angle_distance_sum+=min(angle, (-1.0*(angle-180.0)))
##            print angle,(-1.0*(angle-180.0)), min(angle, (-1.0*(angle-180.0)))
##        print angle_distance_sum
        if((angle_distance_sum/self.size) > tolerance):
            return False
        else:
            return True


   
    def isClusterRegular2(self, tolerance):
        for i in xrange(self.size):
            for j in xrange(self.size-1-i):
                ## If distance of any two particles from CM is different and larger then tolerance cluster is not regular
                if( math.fabs((self.__particleList[i][0].pos-self.com).norm() - (self.__particleList[j][0].pos-self.com).norm()) >= tolerance):
                    return False
        return True

    def isClusterRegular3(self, tolerance):
        if(self.size == 3):
            tolerance+=0.3

        if(self.size == 4):
            tolerance+=10.0
        if(self.size == 5):
            tolerance+=0.0
            
        ## In regular cluster all particles are at about same distance form COM ....
        ## so if any distance of particle form COM is too diferent from first particle distance its not a regular cluster
        first_dist = (self.__particleList[0][0].pos-self.cmass).norm()
        for particle in self.__particleList[1:]:
            if( math.fabs((particle[0].pos-self.cmass).norm()-first_dist) > tolerance):
                return False
        return True

    def isClusterRegular4(self, tolerance):
        ## Lets make sum of patch vector distances from COM, if all patches point to center of cluster SUM is close to zero
        distance_sum = 0.0
        for particle in self.__particleList:
            particle_distance_to_COM = (particle[0].pos-self.cmass).norm()
            distance_sum+=((particle[0].dir*particle_distance_to_COM)-self.cmass)
            if( math.fabs((particle[0].pos-self.cmass).norm()-first_dist) > tolerance):
                return False
        return True

    def isClusterParallel(self, tolerance):
        for i in xrange(self.size):
            for j in xrange(self.size-1-i):
                ## count angles between all different particles
                angle = math.fabs(math.degrees(self.__particleList[i][0].dir.Angle(self.__particleList[j+i+1][0].dir)))
                if(min(angle, (-1.0*(angle-180.0))) >= tolerance):
                    return False
        return True

    def Translate(self, tr_vector):
        if(issubclass(tr_vector.__class__, vec)):
            for particle in self.__particleList:
                particle[0].Translate(tr_vector)
            self.__CENTEROFMASS()
        else:
            raise Exception("Translation of cluster can be done only with 3D vector!")

    def CenterCluster(self, box):
        ## Center particle in box
        center_of_box=vec3([i/2.0 for i in box]);
        ## translate cluster so first particle is in center
        tr_vec=center_of_box-self.__particleList[0][0].pos
        self.Translate(tr_vec)
        self.UsePBC(box)
        self.__CENTEROFMASS()
        ## Now translate pocluster so that center of mass is in center of box
        tr_vec=center_of_box-self.com
        self.Translate(tr_vec)

    def Rotate(self):
        pass




class MovieFrame(object):
    def __init__(self, sweep=0, box=[0.0, 0.0, 0.0]):
        self.__SETSWEEP(sweep)
        self.__SETBOX(box)
        self.__config = []

    def __SETSWEEP(self, sweep):
        if(type(sweep) == int):
            self.__sweep  = sweep
        else:            
            raise Exception("Error: Wrong type of sweep!")

    def __SETCONFIG(self, config):
        if(type(config) == list):
            self.__config = config
        else:
            raise Exception("Error: Wrong type of config!")

    def __SETBOX(self, box):
        self.__box = vec3(box)


    def SetSweep(self, sweep):
        self.__SETSWEEP(sweep)

    def SetBox(self, box):
        self.__SETBOX(box)

#    def SetConfig(self, config):
#        self.__SETCONFIG(config)

    def append(self, data):
        if(type(data) == ParticleConf):
            self.__config.append(data)
        else:
            raise Exception("Apended date are in formate of ParticleConf")

    def Show(self):
        output = self.__HEADSTRING()
        for particle in self.__config:
            output += str(particle)+"\n"
        return output

    def __HEADSTRING(self):
        output = str(len(self.__config))+"\n" ## add number of particles
        output += "sweep %i" % (self.__sweep)+"; box "+"%13g %13g %13g" % (self.__box.x, self.__box.y, self.__box.z)+"\n"
        return output



def movieToCluster(movie_file, cluster_dict, cluster_energy, box):
    box=[float(i) for i in box]
    box_center=vec3([i/2.0 for i in box])
    
    clusters = {}
    while True:
        movie_line = movie_file.readline()
        if not movie_line: break
        line_parts = movie_line.split()
        if (line_parts[0] == "sweep" and line_parts[1] == cluster_dict["sweep"]+";"):
            ## now go through all particles in dict
            for i in xrange(len(cluster_dict)-1):## -1 case there is also sweep!!
                movie_line = movie_file.readline()
                if cluster_dict[i+1] in clusters:
                    clusters[cluster_dict[i+1]].append(movie_line)
                else:
                    clusters.update({cluster_dict[i+1]:[movie_line]})
            ## now create cluster list in format [sweep, ParticleCluster(), ParticleCluster()...]
            new_clusters = [cluster_dict["sweep"]]
            for cl in clusters:
                cl_object = ParticleCluster();
                cl_object.energy=cluster_energy[cl];
                for particles_str in clusters[cl]:
                    cl_object.append(ParticleConf(particles_str), 1.0);
                cl_object.UsePBC(box)
                cl_object.CenterCluster(box)
                #tr=box_center-cl_object.com
                #cl_object.Translate(tr)
                #cl_object.UsePBC(box)
                new_clusters.append(cl_object)
            #print new_clusters[10].size
            return new_clusters
    return False


def main(cluster_file_PATH, movie_file_PATH, box):
    box=box.split()
    ##  TODO: add exception if files exists!
    cluster_file = open(cluster_file_PATH, 'r')
    movie_file   = open(movie_file_PATH, 'r')

    current_sweep = 0 # Keep information about sweep number from cluster.dat
    cluster_dict  = {}
    clusters_all = []

    while True:
        cluster_line = cluster_file.readline()
        if not cluster_line: break        
        ## TODO: strip coments ... strcto do jednote funkce read line
        line_parts = cluster_line.split()
        if (line_parts[0] == "Sweep:" ): #this is first line of sweep
            if (cluster_dict):
                ##call function to read movie                
                new_clusters = movieToCluster(movie_file, cluster_dict, cluster_energy, box)
                if(new_clusters):
                    clusters_all.append(new_clusters)              
            cluster_id = 1
            cluster_dict = {}
            cluster_energy ={}
            cluster_dict.update({"sweep":line_parts[1]})
            cluster_line = cluster_file.readline()
            line_parts = cluster_line.split()
        #GET energy of cluster
        energy = float(line_parts[0].split('(')[1].split(')')[0])
        cluster_energy.update({cluster_id:energy})
        for i in xrange(len(line_parts) - 1): ## now fill one cluster on line into cluster_dict
            cluster_dict.update({int(line_parts[i+1]):cluster_id})
#            print line_parts[i+1]
        cluster_id+=1
    output_data = {"files":{}}
    ## make statistics for each sweep
    max_size=0
    for sweep in clusters_all:
        output_data.update({int(sweep[0]):{}})
        for cluster in sweep[1:]:
            if(cluster.size > max_size):
                max_size=cluster.size
            if(cluster.size in output_data[int(sweep[0])]):
                #if(cluster.isClusterParallel(ANGLE_TOLERANCE) and (math.fabs((cluster.energy/cluster.size)-CLUSTER_ENERGY) < (CLUSTER_ENERGY_TOLERANCE*cluster.size) )):
                ## Special for tetramer from two dimers
                #if(cluster.isClusterParallel(ANGLE_TOLERANCE) and not cluster.arePatchsPointingToCOM2(PATCH_ANGLE_TOLERANCE,box) and (math.fabs((cluster.energy/cluster.size)-CLUSTER_ENERGY) < (CLUSTER_ENERGY_TOLERANCE*cluster.size) )):
                if(cluster.arePatchsPointingToCOM2(PATCH_ANGLE_TOLERANCE,box) and cluster.isClusterParallel(ANGLE_TOLERANCE) and (math.fabs((cluster.energy/cluster.size)-CLUSTER_ENERGY) < (CLUSTER_ENERGY_TOLERANCE*cluster.size) )):
                #if(cluster.arePatchsPointingToCOM_TCPSC(PATCH_ANGLE_TOLERANCE,box,TCPSC_ANGLE) and cluster.isClusterParallel(ANGLE_TOLERANCE) and cluster.isClusterRegular2(DISTANCE_FROM_COM_TOLERANCE) and (math.fabs((cluster.energy/cluster.size)-CLUSTER_ENERGY) < (CLUSTER_ENERGY_TOLERANCE*cluster.size) )):
                    output_data[int(sweep[0])][cluster.size]['r']+=1;                    
                    output_data["files"][cluster.size]["out_r"].write(cluster.MovieFrame(output_data["files"][cluster.size]["r_count"],box).Show())
                    output_data["files"][cluster.size]['r_count']+=1;
                else:
                    output_data[int(sweep[0])][cluster.size]['i']+=1;
                    output_data["files"][cluster.size]["out_i"].write(cluster.MovieFrame(output_data["files"][cluster.size]["i_count"],box).Show())
                    output_data["files"][cluster.size]['i_count']+=1;
            else:
                #if(cluster.isClusterParallel(ANGLE_TOLERANCE) and (math.fabs((cluster.energy/cluster.size)-CLUSTER_ENERGY) < (CLUSTER_ENERGY_TOLERANCE*cluster.size) )):
                ## Special for tetramer from two dimers
                #if(cluster.isClusterParallel(ANGLE_TOLERANCE) and not cluster.arePatchsPointingToCOM2(PATCH_ANGLE_TOLERANCE,box) and (math.fabs((cluster.energy/cluster.size)-CLUSTER_ENERGY) < (CLUSTER_ENERGY_TOLERANCE*cluster.size))):
                if(cluster.arePatchsPointingToCOM2(PATCH_ANGLE_TOLERANCE,box) and cluster.isClusterParallel(ANGLE_TOLERANCE) and (math.fabs((cluster.energy/cluster.size)-CLUSTER_ENERGY) < (CLUSTER_ENERGY_TOLERANCE*cluster.size) )):
                #if(cluster.arePatchsPointingToCOM_TCPSC(PATCH_ANGLE_TOLERANCE,box,TCPSC_ANGLE) and cluster.isClusterParallel(ANGLE_TOLERANCE) and cluster.isClusterRegular2(DISTANCE_FROM_COM_TOLERANCE) and (math.fabs((cluster.energy/cluster.size)-CLUSTER_ENERGY) < (CLUSTER_ENERGY_TOLERANCE*cluster.size) )):
                    output_data[int(sweep[0])].update({cluster.size:{'r':1,'i':0}})
                    if(not (cluster.size in output_data["files"])):
                        output_data["files"].update({cluster.size:{"r_count":1, "out_r":open("Cluster_size"+str(cluster.size)+"_r", 'a'), "i_count":0, "out_i":open("Cluster_size"+str(cluster.size)+"_i", 'a')}})
                    output_data["files"][cluster.size]["out_r"].write(cluster.MovieFrame(output_data["files"][cluster.size]["r_count"],box).Show())
                    output_data["files"][cluster.size]['r_count']+=1;
                else:
                    output_data[int(sweep[0])].update({cluster.size:{'r':0,'i':1}})
                    if(not (cluster.size in output_data["files"])):
                        output_data["files"].update({cluster.size:{"r_count":0, "out_r":open("Cluster_size"+str(cluster.size)+"_r", 'a'), "i_count":1, "out_i":open("Cluster_size"+str(cluster.size)+"_i", 'a')}})
                    output_data["files"][cluster.size]["out_i"].write(cluster.MovieFrame(output_data["files"][cluster.size]["i_count"],box).Show())
                    output_data["files"][cluster.size]['i_count']+=1;
    out_string=""
    for sweep in sorted(output_data)[:-1]:## dont want to print files part
        out_string+="%9i\t" %(sweep)
        num_of_all_clusters=0.0
        for size in output_data[sweep]:
            num_of_all_clusters+=output_data[sweep][size]['i']
            num_of_all_clusters+=output_data[sweep][size]['r']
        ## now construct output
        for size in range(max_size+1)[1:]:
            if(size in output_data[sweep]):
                out_string+="%20.10e " % (1.0*output_data[sweep][size]['i']/num_of_all_clusters)
                out_string+="%20.10e\t" % (1.0*output_data[sweep][size]['r']/num_of_all_clusters)
            else:
                out_string+="%20.10e %20.10e\t" % (0.0, 0.0)
        out_string+="\n"
    print out_string
    cluster_file.close();
    movie_file.close();
    return 0;

def usepbc(pos,pbc):
    newpos = []
    for coord in pos:
        i=pos.index(coord)
        newcoord=coord
        while newcoord < 0:
            newcoord = newcoord + pbc[i]
        while newcoord > pbc[i]:
            newcoord = newcoord - pbc[i] 
        newpos.append(newcoord)
    return newpos

def test():
    cl=ParticleCluster()
    cl2=ParticleCluster()
    soub=open("./test_trimer", 'r')
    for l in soub:
        if(len(l.split()) > 9):
            cl.append(ParticleConf(l), 1.0)
            particle=ParticleConf(l)
            particle.pos=vec3(usepbc(particle.pos._vec__values, [25,25,25]))
            cl2.append(particle, 1.0)
    cl.UsePBC([25,25,25])
    print cl.arePatchsPointingToCOM_TCPSC(PATCH_ANGLE_TOLERANCE,[25,25,25],40.0)
    print "-----------------------"
    cl2.arePatchsPointingToCOM2(30.0,[25,25,25])
    

parser=optparse.OptionParser()
help="""Usage:
%prog [options] 
"""
parser.set_usage(help)
parser.add_option(
    "-c",
    "--cluster",
    help="Set path to cluster.dat file.",
    dest="cluster_file_PATH",
    )
parser.add_option(
    "-m",
    "--movie",
    help="Set path to movie file.",
    dest="movie_file_PATH",
    )
parser.add_option(
    "-b",
    "--box",
    help="Set size of simulation box.",
    dest="box",
    )
(options,arguments)=parser.parse_args()
main(options.cluster_file_PATH, options.movie_file_PATH, options.box)

