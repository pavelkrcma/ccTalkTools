ccTalkTools, a collection of tools to interact with a ccTalk bus

Forked from https://github.com/Baldanos/ccTools and made Python3 compatible
ccParse now could load text logs, useful for debugging 3rd party applications
UV is the preffered package manager

= Tools

== ccParse
ccParse can read a data dump made by ccSniff or other dumper to actually parse the data in a more comprehensive way.
Just launch ccParse with a dump file as a parameter (see the help).

ccParse uses the urwid library.

== ccSniff
ccSniff is meant to be used as a ccTalk bus sniffer. Just connect a UART (like a bus pirate) and start ccSniff.

Usage: ccSniff.py [options]

Options:
  -h, --help            show this help message and exit
  -i DEVICE, --interface=DEVICE
                        Serial port to use
  -w FILE, --write=FILE
                        File name to write data
  -b, --bus-pirate      Use this switch to tell the serial port is a bus
                        pirate

The ccTalk messages will be displayed in the console.

== ccJack
ccJack is used to hijack a ccTalk device on a bus. You will need a UART with both RX and TX connected to the but for it to work.
ccJack works by firstly listening for data, then learn responses made by the device to be hijacked. Then it sends out an "Address change" request to the device and starts to respond instead of the hijacked device.

Usage: ccJack.py [options]

Options:
  -h, --help            show this help message and exit
  -i DEVICE, --interface=DEVICE
                        Serial port to use
  -b, --bus-pirate      Use this switch to tell the serial port is a bus
                        pirate
  -s SOURCE, --source=SOURCE
                        Source address of the device to hijack
  -d DESTINATION, --destination=DESTINATION
                        Destination address of the device to hijack
  -t TIME, --time=TIME  Time to listen for packets
  -r FILE, --read=FILE  File to read responses from

You can optionaly provide a ccSniff capture file for ccJack to learn responses. As responses can sometimes change, it will always take the last responses it read on the bus.
