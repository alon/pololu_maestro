import serial
import time
import sys
import shelve
import usb

import usb_util

#servos = shelve.open('servos.shelve')

MAESTRO_VENDOR_ID, MAESTRO_PRODUCT_ID = 0x1ffb, 0x0089

# Request enum from Usc_protocol.cs
class uscRequest(object):
	REQUEST_GET_PARAMETER = 0x81
	REQUEST_SET_PARAMETER = 0x82
	REQUEST_GET_VARIABLES = 0x83
	REQUEST_SET_SERVO_VARIABLE = 0x84
	REQUEST_SET_TARGET = 0x85
	REQUEST_CLEAR_ERRORS = 0x86
	REQUEST_REINITIALIZE = 0x90
	REQUEST_ERASE_SCRIPT = 0xA0
	REQUEST_WRITE_SCRIPT = 0xA1
	REQUEST_SET_SCRIPT_DONE = 0xA2
	REQUEST_RESTART_SCRIPT_AT_SUBROUTINE = 0xA3
	REQUEST_RESTART_SCRIPT_AT_SUBROUTINE_WITH_PARAMETER = 0xA4
	REQUEST_RESTART_SCRIPT = 0xA5
	REQUEST_START_BOOTLOADER = 0xFF

class Usb(object):
	def __init__(self):
		self._device = usb_util.get_device(MAESTRO_VENDOR_ID)
		interface = self._device.configurations[0].interfaces[4][0]
		print "using interface with class %s (%s)" % (interface.interfaceClass,
			usb_util.interfaceClass2string[interface.interfaceClass])
		self._handle = usb_util.get_handle(self._device, interface)

	def controlTransfer(self, requestType, request, value, index, data=''):
		"""
		controlMsg(requestType, request, buffer, value=0, index=0, timeout=100) -> bytesWritten|buffer
    
		Performs a control request to the default control pipe on a device.
		Arguments:
		        requestType: specifies the direction of data flow, the type
		    		 of request, and the recipient.
		        request: specifies the request.
		        buffer: if the transfer is a write transfer, buffer is a sequence 
		    	    with the transfer data, otherwise, buffer is the number of
		    	    bytes to read.
		        value: specific information to pass to the device. (default: 0)
		        index: specific information to pass to the device. (default: 0)
		        timeout: operation timeout in miliseconds. (default: 100)
		Returns the number of bytes written.

		"""
		return self._handle.controlMsg(requestType=requestType, request=request,
					value=value, index=index, buffer=data, timeout=5000)

	def getRawParameter(self):
		self.controlTransfer(0xC0, uscRequest.REQUEST_GET_PARAMETER, 0, parameter, array)

	def setTarget(self, servo, value):
		self.controlTransfer(0x40, uscRequest.REQUEST_SET_TARGET, value, servo)

SET_TARGET = 0x84

STEPS = 10

def bytes2str(bytes):
	return ''.join(map(chr, bytes))

def target_command(servo, target):
	""" target in microseconds """
	if not (0 <= servo <= 6):
		print "error: bad servo value %s" % servo
		raise SystemExit
	target = target * 4 # quarter microseconds
	high = (int(target)/128) & 0x7f
	low = target & 0x7f
	cmd = bytes2str([0xAA, 12, SET_TARGET & 0x7f, servo, low, high])
	print "setting %s to %s, %s (%s) %r" % (target, high, low, target, cmd)
	# Basic protocol?
	#return ''.join([chr(x) for x in [SET_TARGET, servo, high, low]])
	# When more then one device is connected
	return cmd
	# Mini SSC protocol
	#return bytes2str([0xFF, servo, target & 0xff])

def get_position(servo):
	return bytes2str([0x90, servo])

def move(servo, start, end):
	for i in xrange(STEPS):
		s.write(target_command(servo=servo, target=(end - start)*i/(STEPS-1) + start))
		time.sleep(1.0/STEPS)

def move_main():
	if len(sys.argv) == 3:
		servo, start = map(int, sys.argv[-2:])
		end = start
	elif len(sys.argv) != 4:
		print "usage: %s <servo> <start> <end>" % sys.argv[0]
		servo, start, end=map(int, sys.argv[-3:])
		raise SystemExit
	u = Usb()
	u.setTarget(servo=servo, value=start)
	#move(servo=servo, start=start, end=end)

if __name__ == '__main__':
	#s = serial.Serial('/dev/ttyACM0')
	move_main()

