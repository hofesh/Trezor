# system requirements
- python 2.7
- Mac OSX (should work on Linux, but proper dependencies must be installed for "make build_unix" to work)

# install python-trezor
git clone https://github.com/trezor/python-trezor
cd python-trezor
sudo python setup.py install

# build trezor-core
git clone https://github.com/trezor/trezor-core
cd trezor-core
git submodule update --init
brew install scons sdl2 sdl2_image
make build_unix

# run emulator
./emu.sh

# confirm that python-trezor can communicate with trezor-core
# (-t udp tells trezorctl to not look for trezor on usb, but rather on udp- emulator uses udp sockets instead of usb)
cd python-trezor
trezorctl -t udp get_features

# You should see output similar to this:
Features {
    vendor: "trezor.io"
    major_version: 2
    minor_version: 0
    patch_version: 0
...
    initialized: true
    revision: "0123456789"
    bootloader_hash: "0123456789"
}


# download pwdreader.py
wget https://raw.githubusercontent.com/satoshilabs/slips/master/slip-0016/pwdreader.py

# Change line
from trezorlib.transport_hid import HidTransport
# to
from trezorlib.transport_udp import UdpTransport

# Change lines
    devices = HidTransport.enumerate()
    if not devices:
        print('TREZOR is not plugged in. Please, connect TREZOR and retry.')
        return

    client = TrezorClient(devices[0])
# to
    client = TrezorClient(UdpTransport())
	

# Unfortunately Recovery process is not implemented yet in TREZORv2, so you would need to load the device using full mnemonic - if you are not OK with typing your mnemonic into the computer (and you should not be as it holds all your coins), don't do it!
trezorctl -t udp load_device -m "this is my mnemonic sentence ..."

# Once you have TREZORv2 emulator loaded with your seed, you can run the modified pwdreader.py which will connect to the emulator and decode the Password Manager storage - it looks for files in $(HOME)Dropbox/Apps/TREZOR Password Manager, so make sure you have files there
pwdreader.py

