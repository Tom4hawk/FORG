# Quick module to test the List and ListNode classes.

from List import *
from ListNode import *

def p(x):
    print x.getData()

def makenode(y):
    return ListNode("The number is: %d" % y)

nodes = map(makenode, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])

lst = List()
for node in nodes:
    lst.insert(node)

try:
    lst.getNext()
    lst.getNext()
    lst.getNext()
    lst.getNext()
    lst.getNext()
except:
    pass

try:
    lst.getPrev()
    lst.getPrev()
    lst.getPrev()
except:
    pass


lst.insert(ListNode("foo"), None)
lst.insert(ListNode("bar"), None)
lst.insert(ListNode("Baz"), None)
    
lst.traverse(p) # Prints all numbers to 15

try:
    p(lst.getNext())
except:
    print "Can't get next item."

print "==================="

p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
p(lst.getPrev())
