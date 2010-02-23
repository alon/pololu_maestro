import usb

def get_device(vendorid):
    busses = usb.busses() # enumerate, takes a little while
    devices = sum([[y for y in x.devices if y.idVendor == vendorid] for x in busses], [])
    if len(devices) == 0:
        return None
    return devices[0]

def get_interface(configuration, which_class):
    return sum([[i for i in ifs if i.interfaceClass == which_class] for ifs in configuration.interfaces], [])

def get_handle(device, interface):
    handle = device.open()
    handle.claimInterface(interface)
    return handle

interfaceClass2string = dict([(getattr(usb, x), x) for x in dir(usb) if x[:6] == 'CLASS_'])

