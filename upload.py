from optparse import OptionParser
import serial
import xmodem
import os, sys, time
import logging
import pyprind
import platform

logging.basicConfig()
parser = OptionParser(usage="python %prog [options]")
parser.add_option("-f", dest="bin_path", help="path of bin to be upload")
if platform.system() == 'Windows':
    parser.add_option("-c", dest="com_port", help="COM port, can be COM1, COM2, ..., COMx")
else:
    parser.add_option("-c", dest="port", help="USB port, can be /dev/tty.XXXX")
parser.add_option("-b", dest="baud_rate", help="Baud rate, can be 9600, 115200, etc...", type="int", default=115200)
(opt, args) = parser.parse_args()

if not os.path.exists(opt.bin_path):
    print >> sys.stderr, "\nError: File [ %s ] not found !!!\n" % (opt.bin_path)
    parser.print_help()
    sys.exit(-1)

def init():
    print >> sys.stderr, "Please push the Reset button"

    flag = 1
    while flag:
        c = s.read()
        if c =='C':
            flag = 0
            pass
        pass

    print >> sys.stderr, "Reset button pushed, start uploading bootloader"
    statinfo = os.stat('./bootloader.bin')
    bar = pyprind.ProgBar(statinfo.st_size/128+1)

    def getc(size, timeout=1):
        return s.read(size)

    def putc(data, timeout=1):
        bar.update()
        return s.write(data)

    def putc_user(data, timeout=1):
        bar_user.update()
        return s.write(data)

    def pgupdate(read, total):
        print "\r%d/%d bytes (%2.f%%) ..." % (read, total, read*100/total)

    m = xmodem.XMODEM(getc, putc)
    stream = open('./bootloader.bin', 'rb')
    m.send(stream)

    print >> sys.stderr, "Bootloader uploaded, start uploading user bin"
    time.sleep(1)
    s.write("2\r")
    s.flush()
    s.flushInput()

    flag = 1
    while flag:
        c = s.read()
        if c =='C':
            flag = 0
            pass
        pass
    s.flush()
    s.flushInput()

    statinfo_bin = os.stat(opt.bin_path)
    bar_user = pyprind.ProgBar(statinfo_bin.st_size/128+2)
    stream = open(opt.bin_path, 'rb')
    m = xmodem.XMODEM(getc, putc_user)
    m.send(stream)

    print >> sys.stderr, "Program uploaded, starting the program"
    time.sleep(1)
    s.write("C\r")
    s.flush()
    s.flushInput()

if platform.system() == 'Windows':
    if not opt.bin_path or not opt.com_port:
        print >> sys.stderr, "\nError: Invalid parameter!! Please specify COM port and bin.\n"
        parser.print_help()
        sys.exit(-1)

    s = serial.Serial(opt.com_port, 115200)
    init()

else:
    if not opt.bin_path or not opt.port:
        print >> sys.stderr, "\nError: Invalid parameter!! Please specify COM port and bin.\n"
        parser.print_help()
        sys.exit(-1)

    s = serial.Serial(opt.port, 115200)
    init()