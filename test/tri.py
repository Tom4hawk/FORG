from GopherConnection import *
from GopherResource import *
from ResourceInformation import *

res = GopherResource()
res.setHost("mothra")
res.setPort(70)
res.setLocator("1/Source code")
res.setName("Source code")

conn = GopherConnection()
resinfo = conn.getInfo(res)

print resinfo.toString()
