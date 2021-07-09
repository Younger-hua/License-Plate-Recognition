from comm.comfunction import COMMFUNCS
class CarManage:
    def Enter(self, car):
        conn = COMMFUNCS.getConnection()
        cur = conn.cursor()
        cur.execute(
            "insert into car(CarPN,TimeIn,TimeOut,PayVal) values('%s','%s','%s',%f)" % (car.CarPN, car.TimeIn, car.TimeOut, car.PayVal))
        conn.commit()
        print("enter ok!")

    def Leave(self,car):
        conn = COMMFUNCS.getConnection()
        cur = conn.cursor()
        cur.execute("select * from car where CarPN = '%s' and TimeOut = ''" % car.CarPN)
        results = cur.fetchall()
        return  results

    def Update(self,car):
        conn = COMMFUNCS.getConnection()
        cur = conn.cursor()
        cur.execute("update car set TimeOut='%s',PayVal='%.2f' where CarPN='%s' and TimeOut = ''" % (car.TimeOut,car.PayVal,car.CarPN))
        conn.commit()
        print("update ok!")