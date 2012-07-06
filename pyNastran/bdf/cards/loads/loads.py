# pylint: disable=C0103,R0902,R0904,R0914
import sys
from pyNastran.bdf.cards.baseCard import BaseCard

class Load(BaseCard):
    """defines the DefaultLoad class"""
    type = 'DefLoad'
    def __init__(self, card, data):
        pass

    def Cid(self):
        if isinstance(self.cid, int):
            return self.cid
        else:
            return self.cid.cid
        ###

    def nodeIDs(self, nodes=None):
        """returns nodeIDs for repr functions"""
        if not nodes:
            nodes = self.nodes
        if isinstance(nodes[0], int):
            return [node     for node in nodes]
        else:
            return [node.nid for node in nodes]
        ###

    def rawFields(self):
        fields = [self.type, self.lid]
        return fields

    def reprFields(self):
        return self.rawFields()


class LSEQ(BaseCard): # Requires LOADSET in case control deck
    """
    Defines a sequence of static load sets
    @todo how does this work...
    """
    type = 'LSEQ'
    def __init__(self, card=None, data=None):
        if card:
            self.sid  = card.field(1)
            self.exciteID = card.field(2)
            self.lid = card.field(3)
            self.tid = card.field(4)
        else:
            self.sid = data[0]
            self.exciteID = data[1]
            self.lid = data[2]
            self.tid = data[3]
            raise NotImplementedError()

    def nodeIDs(self, nodes=None):
        """returns nodeIDs for repr functions"""
        if not nodes:
            nodes = self.nodes
        if isinstance(nodes[0], int):
            return [node     for node in nodes]
        else:
            return [node.nid for node in nodes]
        ###

    def crossReference(self, model):
        self.lid = model.Load(self.lid)
        if self.tid:
            self.tid = model.Load(self.tid)
        ###
    
    def Lid(self):
        try:
            if isinstance(self.lid, int):
                return self.lid
            elif isinstance(self.lid, list):
                #sys.stderr.write('type(lid[0]) = %s' %(type(self.lid[0])))
                #sys.stderr.write("the offending load...%s" %(self.lid[0]))
                return self.lid[0].lid
            #elif isinstance(self.lid,load)
            else:
                #sys.stderr.write("the offending load...%s" %(self.lid))
                return self.lid.lid
        except:
            msg = "error - line 88 in loads.py - self.lid=\n %s\n" %(str(self.lid))
            sys.stderr.write(msg)
            raise
        
    def Tid(self):
        if self.tid is None:
            return None
        if isinstance(self.tid, int):
            return self.tid
        return self.tid.tid

    def rawFields(self):
        fields = ['LSEQ', self.sid, self.exciteID, self.Lid(), self.Tid()]
        return fields

    def reprFields(self):
        return self.rawFields()

class SLOAD(Load):
    """
    Static Scalar Load
    Defines concentrated static loads on scalar or grid points.
    
    @note Can be used in statics OR dynamics.

    If Si refers to a grid point, the load is applied to component T1 of the
    displacement coordinate system (see the CD field on the GRID entry).
    """
    type = 'SLOAD'
    def __init__(self, card=None, data=None):
        ## load ID
        self.lid = card.field(1)
        
        fields = card.fields(2)
        n = len(fields)//2
        if len(fields)%2 == 1:
            n += 1
            msg = 'missing last magnitude on SLOAD card=%s' %(card.fields())
            raise RuntimeError(msg)

        self.nids = []
        self.mags = []
        for i in range(n):
            j = 2*i
            self.nids.append(fields[j  ])
            self.mags.append(fields[j+1])
        ###

    def Lid(self):
        return self.lid

    def crossReference(self, model):
        for (i, nid) in enumerate(self.nids):
            self.nids[i] = model.Node(nid)
        ###

    def Nid(self, node):
        if isinstance(node, int):
            return node
        return node.nid

    def rawFields(self):
        fields = ['SLOAD', self.lid]
        for (nid, mag) in zip(self.nids, self.mags):
            fields += [self.Nid(nid), mag]
        return fields

    def reprFields(self):
        return self.rawFields()

#---------------------------------------------------------------------
# DLOAD loads

class DLOAD(Load):
    type = 'DLOAD'
    def __init__(self, card=None, data=None):
        ## load ID
        self.lid   = card.field(1)
        self.scale = card.field(2)

        fields = card.fields(3)
        n = len(fields)//2
        if len(fields)%2 == 1:
            n+=1
            msg = 'missing last magnitude on DLOAD card=%s' %(card.fields()) 
            raise RuntimeError(msg)

        self.sids = []
        self.mags = []
        for i in range(n):
            j = 2*i
            self.mags.append(fields[j  ])
            self.sids.append(fields[j+1])  # RLOADx,TLOADx,ACSRC
        ###

    def crossReference(self, model):
        for (i, sid) in enumerate(self.sids):
            self.sids[i] = model.Load(sid)
        ###

    def Sid(self, sid):
        if isinstance(sid, int):
            return sid
        return sid.lid

    def rawFields(self):
        fields = ['DLOAD', self.lid, self.scale]
        for (mag, sid) in zip(self.mags, self.sids):
            fields += [mag, self.Sid(sid)]
        return fields

    def reprFields(self):
        return self.rawFields()

class DAREA(BaseCard):
    """
    Defines scale (area) factors for static and dynamic loads. In dynamic
    analysis, DAREA is used in conjunction with ACSRCE, RLOADi and TLOADi
    entries.
    DAREA SID P1 C1 A1  P2 C2 A2
    DAREA 3   6   2 8.2 15 1  10.1
    """
    type = 'DAREA'
    def __init__(self, card=None, nOffset=0, data=None):
        if card:
            nOffset *= 3
            self.sid   = card.field(1)
            self.p     = card.field(2+nOffset)
            self.c     = card.field(3+nOffset)
            self.scale = card.field(4+nOffset)
        else:
            self.sid   = data[0]
            self.p     = data[1]
            self.c     = data[2]
            self.scale = data[3]
            assert len(data)==4, 'data = %s' %(data)
        ###
        
    def rawFields(self):
        fields = ['DAREA', self.sid, self.p, self.c, self.scale]
        return fields

class TabularLoad(BaseCard):
    def __init__(self, card, data):
        pass

class TLOAD1(TabularLoad):
    """
    Transient Response Dynamic Excitation, Form 1
    Defines a time-dependent dynamic load or enforced motion of the form:
    \f[ {P(t)} = {A} \cdot F(t-\tau) \f]
    for use in transient response analysis.
    """
    type = 'TLOAD1'
    def __init__(self, card=None, data=None):
        TabularLoad.__init__(self, card, data)
        ## load ID
        self.lid   = card.field(1)

        ## Identification number of DAREA or SPCD entry set or a thermal load
        ## set (in heat transfer analysis) that defines {A}. (Integer > 0)
        self.exciteID = card.field(2)

        ## If it is a non-zero integer, it represents the
        ## identification number of DELAY Bulk Data entry that defines . If it
        ## is real, then it directly defines the value of that will be used for
        ## all degrees-of-freedom that are excited by this dynamic load entry.
        ## See also Remark 9. (Integer >= 0, real or blank)
        self.delay = card.field(3)

        ## Defines the type of the dynamic excitation. (LOAD,DISP, VELO, ACCE)
        self.Type = card.field(4, 'LOAD')

        ## Identification number of TABLEDi entry that gives F(t). (Integer > 0)
        self.tid = card.field(5)

        ## Factor for initial displacements of the enforced degrees-of-freedom.
        ## (Real; Default = 0.0)
        self.us0 = card.field(6, 0.0)

        ## Factor for initial velocities of the enforced degrees-of-freedom.
        ## (Real; Default = 0.0)
        self.vs0 = card.field(7, 0.0)
        if   self.Type in [0, 'L', 'LO', 'LOA', 'LOAD']:
            self.Type = 'LOAD'
        elif self.Type in [1, 'D', 'DI', 'DIS', 'DISP']:
            self.Type = 'DISP'
        elif self.Type in [2, 'V', 'VE', 'VEL', 'VELO']:
            self.Type = 'VELO'
        elif self.Type in [3, 'A', 'AC', 'ACC', 'ACCE']:
            self.Type = 'ACCE'
        else:
            msg = 'invalid TLOAD1 type  Type=|%s|' %(self.Type)
            raise RuntimeError(msg)

    def crossReference(self, model):
        if self.tid:
            self.tid = model.Table(self.tid)

    def Tid(self):
        if self.tid == 0:
            return None
        elif isinstance(self.tid, int):
            return self.tid
        return self.tid.tid

    def rawFields(self):
        fields = ['TLOAD1', self.lid, self.exciteID, self.delay, self.Type, self.Tid(), self.us0, self.vs0]
        return fields

    def reprFields(self):
        us0 = self.setBlankIfDefault(self.us0, 0.0)
        vs0 = self.setBlankIfDefault(self.vs0, 0.0)
        fields = ['TLOAD1', self.lid, self.exciteID, self.delay, self.Type, self.Tid(), us0, vs0]
        return fields

class RLOAD1(TabularLoad):
    """
    Defines a frequency-dependent dynamic load of the form
    for use in frequency response problems.
    RLOAD1 SID EXCITEID DELAY DPHASE TC TD TYPE
    \f[ \large \left{ P(f)  \right}  = \left{A\right} [ C(f)+iD(f)]
        e^{  i \left{\theta - 2 \pi f \tau \right} } \f]
    RLOAD1 5   3                     1
    """
    type = 'RLOAD1'
    def __init__(self, card=None, data=None):
        TabularLoad.__init__(self, card, data)
        self.lid      = card.field(1)  # was sid
        self.exciteID = card.field(2)
        self.delay    = card.field(3)
        self.dphase   = card.field(4)
        self.tc    = card.field(5, 0)
        self.td    = card.field(6, 0)
        self.Type  = card.field(7, 'LOAD')

        if   self.Type in [0, 'L', 'LO', 'LOA', 'LOAD']:
            self.Type = 'LOAD'
        elif self.Type in [1, 'D', 'DI', 'DIS', 'DISP']:
            self.Type = 'DISP'
        elif self.Type in [2, 'V', 'VE', 'VEL', 'VELO']:
            self.Type = 'VELO'
        elif self.Type in [3, 'A', 'AC', 'ACC', 'ACCE']:
            self.Type = 'ACCE'
        else:
            msg = 'invalid RLOAD1 type  Type=|%s|' %(self.Type)
            raise RuntimeError(msg)

    def crossReference(self, model):
        if self.tc:
            self.tc = model.Table(self.tc)
        if self.td:
            self.td = model.Table(self.td)
    
    def Tc(self):
        if self.tc == 0:
            return None
        elif isinstance(self.tc, int):
            return self.tc
        return self.tc.tid

    def Td(self):
        if self.td == 0:
            return None
        elif isinstance(self.td, int):
            return self.td
        return self.td.tid

    def rawFields(self):
        fields = ['RLOAD1', self.lid, self.exciteID, self.delay, self.dphase, self.Tc(), self.Td(), self.Type]
        return fields

    def reprFields(self):
        Type = self.setBlankIfDefault(self.Type, 'LOAD')
        fields = ['RLOAD1', self.lid, self.exciteID, self.delay, self.dphase, self.Tc(), self.Td(), Type]
        return fields

class RLOAD2(TabularLoad):
    """
    Defines a frequency-dependent dynamic load of the form
    for use in frequency response problems.
    
    \f[ \large \left{ P(f)  \right}  = \left{A\right} * B(f)
        e^{  i \left{ \phi(f) + \theta - 2 \pi f \tau \right} } \f]
    RLOAD2 SID EXCITEID DELAY DPHASE TB TP TYPE
    RLOAD2 5   3                     1
    """
    type = 'RLOAD2'
    def __init__(self, card=None, data=None):
        TabularLoad.__init__(self, card, data)
        self.lid      = card.field(1)  # was sid
        self.exciteID = card.field(2)
        self.delay    = card.field(3)
        self.dphase   = card.field(4)
        self.tb    = card.field(5, 0)
        self.tp    = card.field(6, 0)
        self.Type  = card.field(7, 'LOAD')

        if self.Type in [0, 'L', 'LO', 'LOA', 'LOAD']:
            self.Type = 'LOAD'
        elif self.Type in [1, 'D', 'DI', 'DIS', 'DISP']:
            self.Type = 'DISP'
        elif self.Type in [2, 'V', 'VE', 'VEL', 'VELO']:
            self.Type = 'VELO'
        elif self.Type in [3, 'A', 'AC', 'ACC', 'ACCE']:
            self.Type = 'ACCE'
        else:
            msg = 'invalid RLOAD2 type  Type=|%s|' %(self.Type)
            raise RuntimeError(msg)

    def crossReference(self, model):
        if self.tb:
            self.tb = model.Table(self.tb)
        if self.tp:
            self.tp = model.Table(self.tp)
    
    def Tb(self):
        if self.tb == 0:
            return None
        elif isinstance(self.tb, int):
            return self.tb
        return self.tb.tid

    def Tp(self):
        if self.tp == 0:
            return None
        elif isinstance(self.tp, int):
            return self.tp
        return self.tp.tid

    def rawFields(self):
        fields = ['RLOAD2', self.lid, self.exciteID, self.delay, self.dphase, self.Tb(), self.Tp(), self.Type]
        return fields

    def reprFields(self):
        Type = self.setBlankIfDefault(self.Type, 0.0)
        fields = ['RLOAD2', self.lid, self.exciteID, self.delay, self.dphase, self.Tb(), self.Tp(), Type]
        return fields

#---------------------------------------------------------------------
# RANDOM loads

class RandomLoad(BaseCard):
    def __init__(self, card, data):
        pass

class RANDPS(RandomLoad):
    """
    Power Spectral Density Specification
    Defines load set power spectral density factors for use in random analysis
    having the frequency dependent form:
    \f[ S_{jk}(F) = (X+iY)G(F) \f]
    """
    type = 'RANDPS'
    def __init__(self, card=None, data=None):
        if card:
            ## Random analysis set identification number. (Integer > 0)
            ## Defined by RANDOM in the Case Control Deck.
            self.lid = card.field(2)
            
            ## Subcase identification number of the excited load set.
            ## (Integer > 0)
            self.j   = card.field(3)
            
            ## Subcase identification number of the applied load set.
            ## (Integer >= 0; K >= J)
            self.k   = card.field(4)
            
            ## Components of the complex number. (Real)
            self.x   = card.field(5)
            self.y   = card.field(6)
            ## Identification number of a TABRNDi entry that defines G(F).
            self.tid = card.field(7, 0)

    def crossReference(self, model):
        if self.tid:
            self.tid = model.Table(self.tid)
    
    def Tid(self):
        if self.tid == 0:
            return None
        elif isinstance(self.tid, int):
            return self.tid
        return self.tid.tid

    def rawFields(self):
        fields = [self.lid, self.j, self.k, self.x, self.y, self.Tid()]
        return fields
