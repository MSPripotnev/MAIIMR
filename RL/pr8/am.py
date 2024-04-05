import numpy as np

class AM:
    def __init__(self, logFile, numSens=6):
        with open(logFile, "r") as f:
            lines=f.readlines()

        self.numSens=numSens
        self.table=[]
        for l in lines:
            if len(l)==0: continue
            arr=[float(v) for v in l.split(", ")]
            arr1, arr2=arr[:numSens], arr[numSens:]
            self.table.append([arr1, arr2])

        # self.filter()
    def findIndex(self, vec):
        T=[rec[0] for rec in self.table]
        dd=[np.linalg.norm(np.subtract(vec, vec2)) for vec2 in T]
        i = np.argmin(dd)
        return i
    def findRecord(self, vec):
        return self.table[self.findIndex(vec)]
    def findControl(self, vec):
        x=self.findRecord(vec)
        return x[1]
    def filter(self):
        T=[]
        for rec in self.table:
            ok=True
            for rec2 in T:
                d = np.linalg.norm(np.subtract(rec[0], rec2[0]))
                d2 = np.linalg.norm(np.subtract(rec[1], rec2[1]))
                if d+d2==0:
                    ok=False
                    break
            if ok: T.append(rec)
        self.table=T