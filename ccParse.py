import sys
import urwid
import binascii
from ccTalk import *
from optparse import OptionParser

#ccParse, a ccTalk data viewer
#Copyright (C) 2012 Nicolas Oberli
#          (C) 2025 Pavel Krcma
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

keys = []
data = ""

class Label (urwid.Text):

    def selectable(self):
        return True

    def keypress(self,  size,  key):
        return key

def reloadContent():
    content = [urwid.AttrMap(w, None, 'focus') for w in keys]
    return content

def main_ui():
    content = urwid.SimpleListWalker(reloadContent())
    messagesList = urwid.ListBox(content)

    palette = [
        ('body','dark cyan', '', 'standout'),
        ('focus','dark red', '', 'standout'),
        ('head','light red', 'black'),
        ]

    menutxt = urwid.Text("Menu bar")
    menufill = urwid.Filler(menutxt)

    infoTxt = urwid.Text("Info panel")
    infoFill = urwid.Filler(infoTxt)

    def keystroke(kinput):
        if type(kinput) == tuple:
            return

        if kinput in ('q', 'Q', 'esc'):
            raise urwid.ExitMainLoop()

        if kinput in ('enter'):
            pos = messagesList.focus_position
            if pos is None:
                return

            if messages[pos].length > 0:
                if messages[pos].payload.header == 0:
                    text = "\n= In response to : " +\
                            messages[pos-1].payload.headerType + "\n" +\
                            str(messages[pos-1]) + "\n"
                    text = text + "\n= Payload decoding \n" +\
                            messages[pos].payload.parsePayload(
                                    messages[pos-1].payload.header) + "\n"
                else:
                    text = "\n= Header " + str(messages[pos].payload.header) +\
                            " (" + messages[pos].payload.headerType + ")\n"
                    text = text + "= Payload decoding \n" +\
                            messages[pos].payload.parsePayload(
                                    messages[pos].payload.header) + "\n"
            else:
                if messages[pos].payload.header == 0:
                    text = "\n= In response to : " +\
                            messages[pos-1].payload.headerType + "\n" +\
                            str(messages[pos-1]) + "\n"
                else:
                    text = "\n= Header " + str(messages[pos].payload.header) +\
                            " (" + messages[pos].payload.headerType + ")\n"

            text = text + "\n= Raw dump of packet \n" +\
                    ' '.join(binascii.hexlify(messages[pos].raw()).decode()[i:i+2] for i in range(0, len(binascii.hexlify(messages[pos].raw()).decode()), 2))
            infoTxt.set_text(text)

    liste = urwid.Pile(
                       [(urwid.LineBox(messagesList)),
                        ('fixed',17,(urwid.LineBox(infoFill))),
                        ])

    header = urwid.AttrMap(urwid.Text('ccParse 0.5 - ' + str(len(keys)) +' messages'), 'head')
    view = urwid.Frame(liste,  header=header)
    loop = urwid.MainLoop(view, palette, unhandled_input=keystroke)
    loop.run()

def load_binary_file(filename):
    try:
        with open(filename, "rb") as f:
            return f.read()
    except IOError as e:
        print(f"Error reading binary file {filename}: {e}")
        sys.exit(1)

# Load from log file in the format:
# 15:45:34 CC: x20
# 15:45:34 CC: 05 00 01 A6 00 -> 01 04 05 00 10 00 02 00 E4
# 15:45:34 CC: 02 00 01 E5 00 -> 01 0B 02 00 30 05 00 05 00 06 08 04 02 04 02 9E
# The speciality is that the first paket has evaluated checksum so 00 means correctly received packet.
# For purposes of the correct parsing we calculate the checksum again
def load_from_log(filename):
    try:
        with open(filename, "r") as f:
            lines = f.readlines()

        binary_data = b''

        # Parse hex data packets
        for line in lines:
            line = line.strip()
            
            # Check if line starts with timestamp and CC header
            if not (len(line) >= 12 and line[2] == ':' and line[5] == ':' and line[8:12] == ' CC:'):
                continue
            
            # Extract the data part after "CC: "
            data_part = line[12:].strip()
            if data_part.startswith('x'): # Skip lines that start with xnn pattern
                continue
            
            if ' -> ' in data_part:
                input_packet, output_packet = data_part.split(' -> ')
                
                input_hex = input_packet.replace(' ', '')
                if input_hex:
                    try:
                        input_hex_data = bytes.fromhex(input_hex)
                    except ValueError as e:
                        print(f"Error parsing hex data '{input_hex}': {e}")
                        continue

                if (input_hex_data[-1] != 0):
                    print(f"Warning: Packet with invalid checksum detected: {input_packet}")
                    continue

                input_hex_data = input_hex_data[:-1]
                chksum = 256-(sum(input_hex_data) % 256)
                binary_data += input_hex_data + bytes([chksum])

                output_hex = output_packet.replace(' ', '')
                if output_hex:
                    try:
                        binary_data += bytes.fromhex(output_hex)
                    except ValueError as e:
                        print(f"Error parsing hex data '{output_hex}': {e}")
                        continue

        return binary_data
        
    except IOError as e:
        print(f"Error reading log file {filename}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option("-b", "--binary", dest="binary_file", metavar="FILE",
                        help="Load FILE in binary mode")
    parser.add_option("-a", "--ascii", dest="log_file", metavar="FILE",
                        help="Load FILE in text mode")
    parser.add_option("-f", "--filter", metavar="NUMBER", type="int", dest="filter_dest", default=None,
                        help="Filter messages to/from device with address NUMBER")
    parser.add_option("-i", "--interactive", action="store_true", dest="interactive", default=False,
                        help="Start in interactive mode")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                        help="Enable verbose output")

    (options, args) = parser.parse_args()

    if not options.binary_file and not options.log_file:
        parser.print_help()
        sys.exit(1)

    if options.binary_file:
        packet_data = load_binary_file(options.binary_file)
    elif options.log_file:
        packet_data = load_from_log(options.log_file)

    print(f"Loaded {len(packet_data)} bytes of data.\n")

    _, messages = parseMessages(packet_data)
    if options.filter_dest is not None:
        messages = [msg for msg in messages if msg.source == options.filter_dest or msg.destination == options.filter_dest]

    if options.interactive:
        keys = [Label(str(message)) for message in messages]
        reloadContent()
        main_ui()

    else:
        # Print only valid and paired messages
        if options.verbose:
            prev_message = None
            for message in messages:
                if prev_message is None:
                    prev_message = message
                    continue
                # Check for request-response pairs and ACK, NAK or BUSY
                if message.payload.header in [0, 5, 6] and message.destination == prev_message.source and message.source == prev_message.destination:
                    print(prev_message)
                    if message.payload.header in [5, 6]:
                        print("= ERROR")
                    print(' '.join(binascii.hexlify(prev_message.raw()).decode()[i:i+2] for i in range(0, len(binascii.hexlify(prev_message.raw()).decode()), 2)),
                          '->',
                          ' '.join(binascii.hexlify(message.raw()).decode()[i:i+2] for i in range(0, len(binascii.hexlify(message.raw()).decode()), 2)))
                    if prev_message.length > 0:
                        print("= Request payload decoding")
                        print(prev_message.payload.parsePayload(
                                prev_message.payload.header))
                    if message.length > 0:
                        print("= Response payload decoding")
                        print(message.payload.parsePayload(
                                prev_message.payload.header))
                    print("")
                    prev_message = None
                else:
                    print('Unexpected message sequence:')
                    print(prev_message)
                    print(message)
                    print("")
                    prev_message = message

        else:
            for message in messages:
                print(message)
