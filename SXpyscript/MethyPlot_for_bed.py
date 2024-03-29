from __future__ import print_function
from __future__ import division
#from numba import jit
import sys, getopt
import gzip
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
plt.switch_backend('PDF')
##@jit

def message():
    print("\n"+"Usage: python **.py --reference-point or --scale-regions [options]"+"\n")
    print("Description:"+"\n"+"\t"+"\t"+"This tool creates methylation level profile over sets of genomic regions."+"\n")
    print("Options:"+"\n")
    print("\t"+"-v, "+"--version"+"\t"+"show program's version number and exit")
    print("\t"+"-h, "+"--help"+"\t"+"show this help message and exit.")
    print("\t"+"--reference-point or --scale-regions"+"\t"+"Reference-point refers to a position within a BED region(e.g., the starting point). In this mode, only those genomicpositions before (upstream) and/or after (downstream) of the reference point will be plotted."+"In the scale-regions mode, all regions in the BED file are stretched or shrunken to the length (in bases) indicated by the user.")
    print("\t"+"-b"+"    <CGmapFiles>"+"\t"+"data files(Support for multiple files, Separated by commas);generated by CGmaptools")
    print("\t"+"-c"+"    <int>"+"\t"+"minimun coverage for C sites.")
    print("\t"+"-S"+"    <string>"+"\t"+"strands orientation could be forward reverse or all.")
    print("\t"+"-G"+"    <bedfiles>"+"\t"+"data files(Support for multiple files, Separated by commas), should be original bed files.")
    print("\t"+"-r"+"    <referencePoint {start or end}>"+"\t"+"The reference point for the plotting could be either the region start (TSS), the region end (TES) of the region.")
    print("\t"+"-u"+"    <upstream distance>"+"\t"+"Distance upstream of the reference-point selected.")
    print("\t"+"-d"+"    <downstream distance>"+"\t"+"Distance downstream of the reference-point selected.")
    print("\t"+"-w"+"    <window size>"+"\t"+"Length, in bases, binSize for averaging the score over the regions length.")
    print("\t"+"-N"+"    <Equally fragment number>"+"\t"+"Equally divided into the region into several fragments.")
    print("\t"+"-l"+"    <legend names>"+"\t"+"Name of the plot legend. (Support for multiple legends)")
    print("\t"+"-o"+"    <outputfiles average data,final matrix>"+"\t"+"File name to save the average data file and final matrix file. (Separated by commas)")
    print("\t"+"-F"+"    <Figure name>"+"\t"+"Name of the plot name. (plot file format is PDF)"+"\n")
    print("An example usage is:"+"\n")
    print("\t"+"python **.py --reference-point -b **.CGmap.gz,**.CGmap.gz... -c minimal coverage<int> -S <forward/reverse/all> -G **.bed,**.bed... -g **.txt,**.txt... -r start/end -u 1000 -d 1000 -w 50 -l **,** -o **_dens,**_matrix -F **.pdf"+"\n")
    print("\t"+"python **.py --scale-regions -b **.CGmap.gz,**CGmap.gz... -c minimal coverage<int> -S <forward/reverse/all> -G **.bed,**.bed... -g **.txt,**.txt... -u 1000 -d 1000 -w 50 -N 100 -l **,** -o **_dens,**_matrix -F **.pdf"+"\n")
    return

opts,args = getopt.getopt(sys.argv[1:],'-h-v-b:-G:-u:-r:-d:-w:-N:-o:-l:-F:-S:-c:',['help','version','scale-regions','reference-point'])
for opt_name,opt_value in opts:
    if opt_name in ('-h','--help'):
        message()
    if opt_name in ('-v','--version'):
        print("**.py 1.0 2019-10-16")
    if opt_name in ('-b'):
        CGmapfile = opt_value
        CGmaplist=CGmapfile.split(",")
    if opt_name in ('-G'):
        bedfile = opt_value
        bedlist=bedfile.split(",")
    if opt_name in ('-u'):
        upstream = opt_value
        up=int(upstream)
        L=str(up/1000)
    if opt_name in ('-d'):
        downstream = opt_value
        down=int(downstream)
        R=str(down/1000)
    if opt_name in ('-r'):
        referencePoint = opt_value
    if opt_name in ('-w'):
        window = opt_value
        windows=int(window)
    if opt_name in ('-N'):
        BlockNum=int(opt_value)
    if opt_name in ('-F'):
        figurename = opt_value
    if opt_name in ('-l'):
        legend = opt_value
        legendname=legend.split(",")
    if opt_name in ('-o'):
        outputfile = opt_value
        outf=outputfile.split(",")
    if opt_name in ('-S'):
        strands = str(opt_value)
    if opt_name in ('-c'):
        ccov = int(opt_value)
    if opt_name not in ('-h,--help,-v,--version,-b,-G,-r,-u,-d,-w,-N,-o,-l,-F,-S,-c,--scale-regions,--reference-point'):
        message()
    #print("Usage: python tmp1.py <--scale-regions or --reference-point> -b <CGmapfiles> -G <bedfiles> -r <referencePoint {start or end}> -u <upstream_distance> -d <downstream_distance> -N <Equal_block_number> -l <legend_names> -o <outputfiles average.matrix> -F <Figure_name>")
Option={}
for option in opts:
    Option[option[0]]=option[1]

"""
region: {'chr1':{'1643':(13,15),'1644':(12,15),...},
         'chr2':{'...'},...}
"""
def CGmapTodict(Input,Strand):
    region={}
    for line in Input:
        col=line.rstrip().split()
        if "forward" in Strand:
            if int(col[7]) >= int(ccov) and "C" in col[1]: 
                if str(col[0]) in region:
                    region[str(col[0])][str(col[2])]=(int(col[6]),int(col[7]))
                else:
                    region[str(col[0])]={}
                    region[str(col[0])][str(col[2])]=(int(col[6]),int(col[7]))
        elif "reverse" in Strand:
            if int(col[7]) >= int(ccov) and "G" in col[1]:
                if str(col[0]) in region:
                    region[str(col[0])][str(col[2])]=(int(col[6]),int(col[7]))
                else:
                    region[str(col[0])]={}
                    region[str(col[0])][str(col[2])]=(int(col[6]),int(col[7]))
        elif "all" in Strand:
            if int(col[7]) >= int(ccov):
                if str(col[0]) in region:
                    region[str(col[0])][str(col[2])]=(int(col[6]),int(col[7]))
                else:
                    region[str(col[0])]={}
                    region[str(col[0])][str(col[2])]=(int(col[6]),int(col[7]))
    return region

def bedMethyStart(bedfile,readdict,windows,up,down):
    metC=0
    sumC=0
    methyList=[]
    bedf=open(bedfile,'r')
    for line in bedf:
        line=line.strip().split()
        sublist=[]
        if line[5] is "+":
            left=int(line[1])-up
            right=int(line[1])+down
            if line[0] in readdict:
                for k in range(left,right,windows):
                    for j in range(k,(k+windows)):
                        if str(j) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(j)][1]
                            metC+=readdict[line[0]][str(j)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for k in range(left,right,windows):
                    sublist.append(np.nan)
            methyList.append(sublist)
        else:
            left=int(line[2])-up
            right=int(line[2])+down
            if line[0] in readdict:
                for k in range(right,left,-windows):
                    for j in range(k,(k-windows),-1):
                        if str(j) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(j)][1]
                            metC+=readdict[line[0]][str(j)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for k in range(right,left,-windows):
                    sublist.append(np.nan)
            methyList.append(sublist)
    return methyList
    bedfile.close()

def bedMethyEnd(bedfile,readdict,windows,up,down):
    metC=0
    sumC=0
    methyList=[]
    bedf=open(bedfile,'r')
    for line in bedf:
        line=line.strip().split()
        sublist=[]
        if line[5] is "+":
            left=int(line[2])-up
            right=int(line[2])+down
            if line[0] in readdict:
                for k in range(left,right,windows):
                    for j in range(k,(k+windows)):
                        if str(j) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(j)][1]
                            metC+=readdict[line[0]][str(j)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for k in range(left,right,windows):
                    sublist.append(np.nan)
            methyList.append(sublist)
        else:
            left=int(line[1])-up
            right=int(line[1])+down
            if line[0] in readdict:
                for k in range(right,left,-windows):
                    for j in range(k,(k-windows),-1):
                        if str(j) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(j)][1]
                            metC+=readdict[line[0]][str(j)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for k in range(right,left,-windows):
                    sublist.append(np.nan)
            methyList.append(sublist)
    return methyList
    bedfile.close()


def bedMethyBody(bedfile,readdict,windows,up,down,Blocknum):
    metC=0
    sumC=0
    methyList=[]
    bedf=open(bedfile,'r')
    for line in bedf:
        line=line.strip().split()
        sublist=[]
        reside=Blocknum-int(((int(line[2])-int(line[1]))%Blocknum))
        blockSize=int(((int(line[2])-int(line[1]))+reside)/Blocknum)
        if line[5] is "+":
            if line[0] in readdict:
                for k in range(int(line[1])-up,int(line[1]),windows):
                    for j in range(k,(k+windows)):
                        if str(j) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(j)][1]
                            metC+=readdict[line[0]][str(j)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for k in range(int(line[1])-up,int(line[1]),windows):
                    sublist.append(np.nan)
            if line[0] in readdict:
                for x in range(int(line[1]),int(line[2])+reside,blockSize):
                    for y in range(x,(x+blockSize)):
                        if str(y) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(y)][1]
                            metC+=readdict[line[0]][str(y)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for x in range(int(line[1]),int(line[2])+reside,blockSize):
                    sublist.append(np.nan)
            if line[0] in readdict:
                for u in range(int(line[2]),int(line[2])+down,windows):
                    for v in range(u,(u+windows)):
                        if str(v) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(v)][1]
                            metC+=readdict[line[0]][str(v)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for u in range(int(line[2]),int(line[2])+down,windows):
                    sublist.append(np.nan)
            methyList.append(sublist)
        else:
            if line[0] in readdict:
                for k in range(int(line[2])+up,int(line[2]),-windows):
                    for j in range(k,(k-windows),-1):
                        if str(j) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(j)][1]
                            metC+=readdict[line[0]][str(j)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for k in range(int(line[2])+up,int(line[2]),-windows):
                    sublist.append(np.nan)
            if line[0] in readdict:
                for x in range(int(line[2]),int(line[1])-reside,-blockSize):
                    for y in range(x,(x-blockSize),-1):
                        if str(y) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(y)][1]
                            metC+=readdict[line[0]][str(y)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for x in range(int(line[2]),int(line[1])-reside,-blockSize):
                    sublist.append(np.nan)
            if line[0] in readdict:
                for u in range(int(line[1]),int(line[1])-down,-windows):
                    for v in range(u,(u-windows),-1):
                        if str(v) in readdict[line[0]]:
                            sumC+=readdict[line[0]][str(v)][1]
                            metC+=readdict[line[0]][str(v)][0]
                        else:
                            pass
                    if sumC == 0:
                        methyratio=np.nan
                    else:
                        methyratio=metC/sumC
                    sublist.append(methyratio)
                    metC=0
                    sumC=0
            else:
                for u in range(int(line[1]),int(line[1])-down,-windows):
                    sublist.append(np.nan)
            methyList.append(sublist)
    return methyList
    bedfile.close()
    
#readdict {'chr1':{'1045':546,''1067:'453',...},...}
#sublist [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8]


#allvalue [[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8],[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8]]
#calculate coordinate start-centered reads
def CGmapToMethyStart(bed,Input,windowSize,strand,Up,Down):
    CGmapf=gzip.open(Input,"rb")
    region=CGmapTodict(CGmapf,strand)
    allvalue=bedMethyStart(bed,region,windowSize,Up,Down)
    return allvalue

#allvalue [[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8],[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8]]
#calculate coordinate end-centered reads
def CGmapToMethyEnd(bed,Input,windowSize,strand,Up,Down):
    CGmapf=gzip.open(Input,"rb")
    region=CGmapTodict(CGmapf,strand)
    allvalue=bedMethyEnd(bed,region,windowSize,Up,Down)
    return allvalue

#bodyvalue [[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8],[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8]]
#calculate up start end down reads
def CGmapToMethyBody(bed,Input,windowSize,strand,Up,Down,BlockNUM):
    CGmapf=gzip.open(Input,"rb")
    region=CGmapTodict(CGmapf,strand)
    bodyvalue=bedMethyBody(bed,region,windowSize,Up,Down,BlockNUM)
    return bodyvalue

def plotsmooth(Values):
    n=len(Values)
    num=range(0,n)
    num=np.array(num)
    xnew=np.linspace(num.min(),num.max(),5*n)
    func=interp1d(num,Values,kind="cubic")
    ynew=func(xnew)
    plt.plot(xnew,ynew)


if "--reference-point" in Option:
    Ylength=int(up+down)
    ylength=int(Ylength/windows)
    left=int(0)
    medium=int(ylength/2)
    right=int(ylength)
    if "-r" in Option and str(referencePoint)=="start":
        out_profile=open(outf[0],"w")
        out_matrix=open(outf[1],"w")
        out_figure=open(figurename,"w")
        figurelist=[]
        for CGmap in range(len(CGmaplist)):
            for Bed in range(len(bedlist)):
                values=CGmapToMethyStart(bedlist[Bed],CGmaplist[CGmap],windows,strands,up,down)
                tup1=np.array(values)
                tup1=tup1.astype(float)
                tup2=np.nanmean(tup1,axis=0)
                figurelist.append(tup2)
                tmpnumber = len(values[0])
                header = ["a" for _ in range(tmpnumber+2)]
                print(*header,sep="\t",end="\n",file=out_matrix)
                for tmp1 in values:
                    print("a","a",*tmp1,sep="\t",end="\n",file=out_matrix)
        print("region","model","value",sep="\t",end="\n",file=out_profile)
        N = 0
        for lis in figurelist:
            n = 0
            for l in lis:
                print(n*windows,legendname[N],l,sep="\t",end="\n",file=out_profile)
                n += 1
            N += 1
        for line in figurelist:
            plotsmooth(line)
        plt.legend(legendname)
        plt.ylabel("Methylation level")
        plt.xticks([left,medium,right],["-"+L+"kb","TSS",R+"kb"])
        plt.savefig(out_figure)    
        out_profile.close()
        out_matrix.close()
        out_figure.close()
    elif "-r" in Option and str(referencePoint)=="end":
        out_profile=open(outf[0],"w")
        out_matrix=open(outf[1],"w")
        out_figure=open(figurename,"w")
        figurelist=[]
        for CGmap in range(len(CGmaplist)):
            for Bed in range(len(bedlist)):
                values=CGmapToMethyEnd(bedlist[Bed],CGmaplist[CGmap],windows,strands,up,down)
                tup1=np.array(values)
                tup1=tup1.astype(float)
                tup2=np.nanmean(tup1,axis=0)
                figurelist.append(tup2)
                tmpnumber = len(values[0])
                header = ["a" for _ in range(tmpnumber+2)]
                print(*header,sep="\t",end="\n",file=out_matrix)
                for tmp1 in values:
                    print("a","a",*tmp1,sep="\t",end="\n",file=out_matrix)
        print("region","model","value",sep="\t",end="\n",file=out_profile)
        N = 0
        for lis in figurelist:
            n = 0
            for l in lis:
                print(n*windows,legendname[N],l,sep="\t",end="\n",file=out_profile)
                n += 1
            N += 1
        for line in figurelist:
            plotsmooth(line)
        plt.legend(legendname)
        plt.ylabel("Methylation level")
        plt.xticks([left,medium,right],["-"+L+"kb","TTS",R+"kb"])
        plt.savefig(out_figure)     
        out_figure.close()
        out_profile.close()
        out_matrix.close()
    else:
        pass
#print("Usage: python tmp1.py <<--scale-regions or --reference-point>> -b <CGmapfile> -G <bedfile> -g <genelist> -r <referencePoint {start or end}> -u <upstream_distance> -d <downstream_distance> -w <window_size> -bn <Equal_block_number> -o <outputfile>")

elif "--scale-regions" in Option:
    left=int(0)
    mediumA=int(up/windows)
    mediumB=mediumA+BlockNum
    right=int(down/windows)+mediumA+BlockNum
    out_profile=open(outf[0],"w")
    out_matrix=open(outf[1],"w")
    out_figure=open(figurename,"w")
    figurelist=[]
    for CGmap in range(len(CGmaplist)):
        for Bed in range(len(bedlist)):
            values=CGmapToMethyBody(bedlist[Bed],CGmaplist[CGmap],windows,strands,up,down,BlockNum)
            tup1=np.array(values)
            tup1=tup1.astype(float)
            tup2=np.nanmean(tup1,axis=0)
            figurelist.append(tup2)
            tmpnumber = len(values[0])
            biaotou = []
            for i in range(0,tmpnumber+2):
                biaotou.append("a")
            print(*biaotou,sep="\t",end="\n",file=out_matrix)
            for tmp1 in values:
                print("a","a",*tmp1,sep="\t",end="\n",file=out_matrix)
    print("region","model","value",sep="\t",end="\n",file=out_profile)
    N = 0
    for lis in figurelist:
        n = 0
        for l in lis:
            print(n*windows,legendname[N],l,sep="\t",end="\n",file=out_profile)
            n += 1
        N += 1
    for line in figurelist:
        plotsmooth(line)
    plt.legend(legendname)
    plt.ylabel("Methylation level")
    plt.xticks([left,mediumA,mediumB,right],["-"+L+"kb","TSS","TTS",R+"kb"])
    plt.savefig(out_figure)
    out_figure.close()
    out_profile.close()
    out_matrix.close()
else:
    pass
