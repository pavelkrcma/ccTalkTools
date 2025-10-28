# ccTalkTools

A collection of tools to interact with a ccTalk bus.

Forked from [https://github.com/Baldanos/ccTools](https://github.com/Baldanos/ccTools), made Python3 compatible and significantly extended.

- ccParse now can load text logs, useful for debugging 3rd party applications
- UV is the preferred package manager

**Note:** There is another interesting related project, a HLA parser for Saleae logic analyser: [https://github.com/RAKKOUCHE/ccTalk-HLA](https://github.com/RAKKOUCHE/ccTalk-HLA)

## Getting Started with UV

This project uses [UV](https://docs.astral.sh/uv/) as the package manager. UV is a fast, modern Python package and project manager that simplifies dependency management.

If you're new to UV, here's how to get started:

1. [**Install UV**](https://docs.astral.sh/uv/getting-started/installation/) 

2. **Sync dependencies** for this project:
   ```bash
   uv sync
   ```
   This will create a virtual environment and install all required dependencies from the `uv.lock` file.

3. **Run the tools** using UV:
   ```bash
   uv run ccParse.py -b examples/ccData.bin -v
   ```

That's it! UV handles the virtual environment and dependencies automatically, so you don't need to manually activate environments or install packages.

## Tools

### ccParse

ccParse can read a data dump made by ccSniff or other dumper to actually parse the data in a more comprehensive way. Just launch ccParse with a dump file as a parameter (see the help). Parameter -i opens the tool in the text UI mode.

ccParse uses the urwid library in the UI mode.

### ccSniff

ccSniff is meant to be used as a ccTalk bus sniffer. Just connect a UART (like a bus pirate) and start ccSniff.

**Usage:**

```
ccSniff.py [options]
```

**Options:**

```
-h, --help            show this help message and exit
-i DEVICE, --interface=DEVICE
                      Serial port to use
-w FILE, --write=FILE
                      File name to write data
-b, --bus-pirate      Use this switch to tell the serial port is a bus
                      pirate
```

The ccTalk messages will be displayed in the console.

### ccJack

ccJack is used to hijack a ccTalk device on a bus. You will need a UART with both RX and TX connected to the bus for it to work.

ccJack works by firstly listening for data, then learning responses made by the device to be hijacked. Then it sends out an "Address change" request to the device and starts to respond instead of the hijacked device.

**Usage:**

```
ccJack.py [options]
```

**Options:**

```
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
```

You can optionally provide a ccSniff capture file for ccJack to learn responses. As responses can sometimes change, it will always take the last responses it read on the bus.
