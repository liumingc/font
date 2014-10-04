#!/usr/bin/env python

import struct
import sys, os

# 2014-09-13 draw the graph ok. decompress ok(it's RLE encoding, not that hard, :-)
# next, convert this to bdf font.

# ht, ascent
# {range-start, range-end, offset, sub-font-file}+ 
def readfont(name):
    print 'reading {0}'.format(name)
    slash = name.rfind('/')
    if slash != -1:
        os.chdir(name[0:slash])
        name = name[slash+1:]
    f = open(name)
    ht, ascent = f.readline().split()
    print 'ht={0}, ascent={1}'.format(ht, ascent)

    global nfonts
    nfonts = 0
    for line in f:
        global rangestart, rangeend, subfontoffset, subfontname
        lst = line.split()
        if len(lst) == 3:
            rangestart, rangeend, subfontname = lst
            rangestart, rangeend = int(rangestart, 16), int(rangeend, 16)
            subfontoffset = 0
        else:
            rangestart, rangeend, subfontoffset, subfontname = lst
            rangestart, rangeend, subfontoffset = int(rangestart, 16), int(rangeend, 16), int(subfontoffset, 16)
        nfonts += rangeend - rangestart + 1
        readsubfont(subfontname)
    f.close()

# subfont ::= image fontheader
# fontheader ::=
#   n[12] ht[12] ascent[12]
#   {x[low-high] top[1] bot[1] left[1] wid[1]} repeat n+1 times

class Fonthdr:
    pass

class Font:
    pass

fonthdr = Fonthdr()

def readsubfont(name):
    print 'reading subfont {0}'.format(name)
    f = open(name)
    data = f.read()
    parseimage(data)
    f.close()

# to simplify, all font are depth 2^0 = 1
def parseimage(data):
    global bdata

    tag = 'compressed'
    if data.find(tag) != -1:
        print 'compressed'
        # skip compressed
        data = data[len(tag)+1:]
        chan, minx, miny, maxx, maxy = struct.unpack('12s12s12s12s12s', data[0:60])
        minx, miny, maxx, maxy = int(minx), int(miny), int(maxx), int(maxy)
        print 'chan={0}, minx={1}, miny={2}, maxx={3}, maxy={4}'.format(chan, minx, miny, maxx, maxy)
        data = data[60:]
        ymax, n = struct.unpack('12s12s', data[0:24])
        ymax, n = int(ymax), int(n)
        print 'ymax={0}, nbytes={1}'.format(ymax, n)
        data = data[24:]
        bdata = decompress(data[0:n])
        print 'fonthdr start: {0}'.format(data[n-16:n+36])
        parsefonthdr(data[n:])
    else:
        # un-test
        chan, minx, miny, maxx, maxy = struct.unpack('12s12s12s12s12s', data[0:60])
        minx, miny, maxx, maxy = int(minx), int(miny), int(maxx), int(maxy)
        print 'chan={0}, minx={1}, miny={2}, maxx={3}, maxy={4}'.format(chan, minx, miny, maxx, maxy)
        bytesinrow = (maxx-minx+7)/8
        rows = maxy - miny
        blen = bytesinrow * rows
        bdata = data[48:48+blen]
        parsefonthdr(data[48+blen:])

    f1 = subfontoffset
    f2 = subfontoffset + rangeend - rangestart
    f3 = subfontoffset + fonthdr.n - 1
    print 'subfont: {0}, f1={1}, f2={2}, len(tab)={3}'.format(subfontname, f1, f2, len(fonthdr.tab))
    drawimage(bdata, fonthdr.tab[f1].x, miny, fonthdr.tab[f3].x + fonthdr.tab[f3].wid, maxy)


def drawimage(bdata, minx, miny, maxx, maxy):
    # draw the bdata
    wid = maxx - minx
    ht = maxy - miny
    for y in range(miny, maxy-1):
        for x in range(minx, maxx):
            bit = getbit(bdata, y, x, wid, ht)
            if bit != 0:
                print '#',
            else:
                print ' ',
        print '' # a newline

def bdfbeg():
  print '''STARTFONT 2.1
FONT -lucm9x15
SIZE 15 75 75
FONTBOUNDINGBOX 9 15 0 -2
STARTPROPERTIES 2
FONT_ASCENT 13
FONT_DESCENT 2
ENDPROPERTIES
CHARS {0}
'''.format(nfonts)

def bdfend():
    print 'ENDFONT'

def bdfsub(s, e):
    pass

def bdfchar(c):
    print '''
STARTCHAR U+{0:04x}
ENCODING {1}
SWIDTH {2} 0
DWIDTH {3} 0
BBX {4} {5} 0 -2
BITMAP
'''.format(c, c,)


def getbit(bdata, y, x, wid, ht):
    bytesinrow = (wid+7)/8
    c = ord(bdata[y*bytesinrow + x/8])
    return (c >> (7 - (x%8))) & 1

def setbit(bdata, y, x, wid, ht):
    pass

def decompress(data):
    pos = 0
    mem = []
    arr = []
#    print 'decompress data, type: {0}'.format(type(data))
    while pos < len(data):
        c = ord(data[pos])
        if c & (1<<7):
            pos += 1
            nbytes = (c & 0x7f) + 1
            tmp = data[pos:pos+nbytes]
            arr += tmp
            mem += tmp
#            print 'copy pos={0}, nbytes={1}'.format(pos, nbytes)
            pos += nbytes
        else:
            nbytes = ((c >> 2) & 0x1f) + 3
            off = (c & 3) * 256 + ord(data[pos+1]) + 1
            for i in range(nbytes):
                x = mem[-off]
                arr.append(x)
                mem.append(x)

#            print 'copy prev, pos={0}, off={1}, nbytes={2}'.format(pos, off, nbytes)
            pos += 2
    print 'decompress {0} bytes'.format(pos)
    return arr
            

def parsefonthdr(data):
    global fonthdr
    fonthdr.n, fonthdr.ht, fonthdr.ascent = struct.unpack('12s12s12s', data[0:36])
    print 'fonthdr: n={0}, ht={1}, ascent={2}'.format(fonthdr.n, fonthdr.ht, fonthdr.ascent)
    fonthdr.n, fonthdr.ht, fonthdr.ascent = int(fonthdr.n), int(fonthdr.ht), int(fonthdr.ascent)
    fonthdr.tab = []
    data = data[36:]
#    print '    x     top     bot    left   width'
    for i in range(fonthdr.n+1):
        xl, xh, top, bot, left, wid = struct.unpack('BBBBBB', data[0:6])
        data = data[6:]
        font = Font()
        font.x, font.top, font.bot, font.left, font.wid = xl + xh*256, top, bot, left, wid
#        print '[{0}] {1} {2} {3} {4} {5}'.format(i, font.x, font.top, font.bot, font.left, font.wid)
        fonthdr.tab.append(font)

#print __name__
if __name__ == '__main__':
    readfont(sys.argv[1])

