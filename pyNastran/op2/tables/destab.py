import os
import sys
import struct
from struct import unpack

#from pyNastran.op2.op2Errors import *
#from pyNastran.bdf.cards.nodes import GRID
#from pyNastran.bdf.cards.coordinateSystems import CORD1R,CORD2R,CORD2C,CORD3G #CORD1C,CORD1S,CORD2S


class DESTAB(object):

    def readDesvar(self,data):
        out = unpack('iiccccccccfff',data[0:28])
        (idvid,dvid,alabel1,bLabel1,cLabel1,dLabel1,alabel2,bLabel2,cLabel2,dLabel2,vmin,vmax,delx) = out
        label1 = alabel1+bLabel1+cLabel1+dLabel1
        label2 = alabel2+bLabel2+cLabel2+dLabel2
        #print "ivid=%s dvid=%s label1=%s label2=%s vmax=%g vmin=%g delx=%g" %(idvid,dvid,label1,label2,vmin,vmax,delx)
        #self.readData(8)

    def readTable_DesTab(self):
        tableName = self.readTableName(rewind=False) # DESTAB
        print "tableName = |%r|" %(tableName)

        self.readMarkers([-1,7],'DESTAB')
        ints = self.readIntBlock()
        #print "*ints = ",ints

        self.readMarkers([-2,1,0],'DESTAB')
        bufferWords = self.getMarker()
        #print "bufferWords = ",bufferWords
        word = self.readStringBlock() # DESTAB
        #print "word = |%s|" %(word)

        iTable = -3
        #imax   = -244
        
        while bufferWords: # read until bufferWords=0
            self.readMarkers([iTable,1,0],'DESTAB')
            nOld = self.n
            bufferWords = self.getMarker()
            #print "bufferWords = ",bufferWords
            if bufferWords==0: # maybe read new buffer...
                self.goto(nOld)
                break
            data = self.readBlock()
            #print "len(data) = ",len(data)
            self.readDesvar(data)
            iTable -= 1

        self.printSection(80)

        #self.op2Debug.write('bufferWords=%s\n' %(str(bufferWords)))
        #print "1-bufferWords = ",bufferWords,bufferWords*4

        #print self.printSection(300)
        #sys.exit('asdf')
