#!/usr/bin/python
import optparse
import sys
import math

def parseColumnSelection(columnsSelection):
    if ( columnsSelection == "all" ):
        return ["all"]
    out = [];
    parsed = columnsSelection.split(",");
    for num in parsed:
        split = num.split("-");
        if ( len(split) == 1 ):
            out.append(int(split[0]));
        else:
            out.extend(range(int(split[0]), int(split[1])+1));
    return out
            
    

def calcStatistics(inputPath, methodType, columnsSelection):
    inputFile = open(inputPath, 'r')
    methodTypeParsed = methodType.split("|");
    
    parsedColumnsSelection = parseColumnSelection(columnsSelection);

    methodsToData={}

    ## read Data
    inputData = [];
    for line in inputFile:
        splits = line.split();
        ## tady dat warning nebo tak neco ... soubor musi byt rectengular
        if len(splits) > 0:
            inputData.append([float(x) for x in splits]);

    ## calculate columnsSum
    columsSum = inputData[0];
    for lineNumber in xrange(1, len(inputData)):
        columsSum = [ columsSum[i] + inputData[lineNumber][i] for i in xrange(len(columsSum)) ];    

    ## calculate mean
    if ( "mean" in methodTypeParsed or "var" in methodTypeParsed  or "std" in methodTypeParsed ):
        columnsMean = [];
        for clSum in columsSum:
            columnsMean.append(clSum/len(inputData));
        methodsToData.update({"mean" : columnsMean});
        #print columnsMean;

    if ( "var" in methodTypeParsed  or "std" in methodTypeParsed ):
        ## calculate variance
        columnsVariance = [ ((inputData[0][i]-columnsMean[i])*(inputData[0][i]-columnsMean[i])) for i in xrange(len(columnsMean)) ];
        for lineNumber in xrange(1, len(inputData)):
            columnsVariance = [ columnsVariance[i]+((inputData[lineNumber][i] - columnsMean[i])*(inputData[lineNumber][i] - columnsMean[i])) for i in xrange(len(columnsMean)) ];
        columnsVariance = [ i/len(inputData) for i in columnsVariance ];
        methodsToData.update({"var" : columnsVariance});
        #print columnsVariance;

    if ( "std" in methodTypeParsed ):
        ## calculate STD
        columnsSTD = [ math.sqrt(i) for i in columnsVariance ];
        methodsToData.update({"std" : columnsSTD});
        #print columnsSTD;


    ## print output
    for i in xrange(len(inputData[0] if (parsedColumnsSelection[0] == "all") else parsedColumnsSelection)):
        for method in methodTypeParsed:
            print "%f " % (methodsToData[method][i]),
        print "  ",
    inputFile.close();    
    
parser=optparse.OptionParser(epilog="Script calculate statistics on data formated in columns.")
parser.set_usage(usage="""%prog [option1] <arg1> [option2] <arg2> ....
""")
parser.add_option(
    "-i",
    "--input",
    help="Tex file with data",
    dest="input"
    )
parser.add_option(
    "-m",
    "--method",
    help="Method to be used.",
    dest="method",
    )
parser.add_option(
    "-c",
    "--columns",
    help="Formated string describing which columns to be used.",
    default="all",
    dest="columns"
    )

(options,arguments)=parser.parse_args()
if not options.input:
    sys.exit("Error: You have to set input file\nFor help type in argument -h or --help")
if not options.method:
    sys.exit("Error: You have to specify method\nFor help type in argument -h or --help")
calcStatistics(options.input,options.method,options.columns)


