import pymysql
class CommFuncs:
    def getConnection(self):
        return pymysql.connect(host='localhost',
    user='root',
    password='lch990704',
    db='car',
    charset='utf8',)

COMMFUNCS = CommFuncs()
