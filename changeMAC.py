# pylama:ignore=E501
from collections import defaultdict
from json import dump, load
from tkinter import Tk, Frame, StringVar, IntVar, OptionMenu, Label, Checkbutton, Button, Entry
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, OpenKey, QueryInfoKey, EnumKey, QueryValueEx

from pytimeparse.timeparse import timeparse

LOCAL_REGISTRY = ConnectRegistry(None, HKEY_LOCAL_MACHINE)


def vivdict(preload=None):
    if preload is None:
        preload = {}
    for key, value in preload.items():
        if isinstance(value, dict):  # Convert all `dict`s to `defaultdict`
            preload[key] = vivdict(value)
    return defaultdict(vivdict, preload)


class MAC():
    def __init__(self, registry):
        self._registry = registry
        self._adaptersKey = OpenKey(self._registry, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}")

    def getNetworkAdapters(self):
        adapters = {}
        for i in range(QueryInfoKey(self._adaptersKey)[0]):
            try:
                subKeyString = EnumKey(self._adaptersKey, i)
                subKey = OpenKey(self._adaptersKey, subKeyString)
                type = QueryValueEx(subKey, '*PhysicalMediaType')[0]
                if type == 14 or type == 9:  # if network adapter
                    try:
                        QueryValueEx(subKey, 'NoDisplayClass')
                    except(Exception):
                        driverDesc = QueryValueEx(subKey, 'DriverDesc')[0]
                        if driverDesc in adapters.keys():
                            adapters[driverDesc+'_'] = subKeyString
                        else:
                            adapters[driverDesc] = subKeyString
            except Exception:
                break
        return adapters

    def setMAC(self, adapterID, newMAC):
        pass  # todo

    def deleteMAC(self, adapterID):
        pass  # todo

    def generateMAC(self, OUI=None):
        pass  # todo


class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self._mac = MAC(LOCAL_REGISTRY)
        self.parent = parent
        self._optionsdict = self._mac.getNetworkAdapters()
        try:
            with open('config.json', 'r') as jsonFile:
                self._config = vivdict(load(jsonFile))
        except FileNotFoundError:
            self._config = vivdict()
        self._build()
        self._currentAdapter = self._optionsdict[self._tkvar1.get()]

    def _build(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=2)
        self.parent.grid_columnconfigure(0, weight=1)
        topframe = Frame(self.parent)
        topframe.grid(sticky='nesw')
        topframe.grid_rowconfigure(0, weight=1)
        topframe.grid_rowconfigure(1, weight=1)
        topframe.grid_columnconfigure(0, weight=2)
        topframe.grid_columnconfigure(1, weight=1)
        bottomframe = Frame(self.parent, relief='raised', borderwidth=1)
        bottomframe.grid_columnconfigure(0, weight=5)
        bottomframe.grid_columnconfigure(1, weight=6)
        bottomframe.grid_rowconfigure(0, weight=1)
        bottomframe.grid_rowconfigure(1, weight=1)
        bottomframe.grid(row=1, column=0, sticky='nesw')
        brightframe = Frame(bottomframe)
        brightframe.grid_rowconfigure(0, weight=1)
        brightframe.grid_rowconfigure(1, weight=1)
        brightframe.grid_columnconfigure(0, weight=1)
        brightframe.grid_columnconfigure(1, weight=1)
        brightframe.grid(row=0, column=1, rowspan=2, sticky='nesw')

        lbl = Label(topframe, text='Network interface')
        lbl.grid(row=0, column=0)
        lbl.bind('<Destroy>', self.saveConfig)

        self._tkvar1 = StringVar(self.parent)
        self._tkvar1.trace('w', self._cbDropdown)
        self._opts = tuple(self._optionsdict.keys())
        OptionMenu(topframe, self._tkvar1, *self._opts).grid(row=1, column=0)

        Button(topframe, text='reset settings', command=self._cbReset).grid(row=1, column=1)

        self._tkvar2 = IntVar(self.parent)
        self._tkvar2.trace('w', self._cbCheckbutton)
        Checkbutton(bottomframe, text='change on restart', variable=self._tkvar2).grid(row=0, column=0)

        Button(bottomframe, text='change MAC', command=self._cbChange).grid(row=1, column=0)

        Label(brightframe, text='OUI').grid(row=0, column=0, padx=7, sticky='e')

        Label(brightframe, text='Expiry time').grid(row=1, column=0, padx=7, sticky='e')

        self._tkvar3 = StringVar(self.parent)
        self._tkvar3.trace('w', self._cbOUI)
        vcmd = (self.register(self._validateOUI), '%P', '%S')
        Entry(brightframe, textvariable=self._tkvar3, validate='key', vcmd=vcmd).grid(row=0, column=1)

        self._tkvar4 = StringVar(self.parent)
        self._tkvar4.trace('w', self._cbExTime)
        Entry(brightframe, textvariable=self._tkvar4).grid(row=1, column=1)

        self._tkvar1.set(self._opts[0])

    def _validateOUI(self, text, change):
        if(change in '0123456789ABCDEF' and len(text) < 7):
            return True
        self.bell()
        return False

    def _cbOUI(self, *args):
        text = self._tkvar3.get()
        if(len(text) == 6):
            self._config['adapterSettings'][self._currentAdapter]['OUI'] = text[0:6]

    def _cbDropdown(self, *args):
        self._currentAdapter = self._optionsdict[self._tkvar1.get()]

        var = self._config['adapterSettings'][self._currentAdapter]['changeOnRestart']
        self._tkvar2.set(var if var != {} else 0)
        var = self._config['adapterSettings'][self._currentAdapter]['OUI']
        self._tkvar3.set(var if var != {} else '')
        var = self._config['adapterSettings'][self._currentAdapter]['expiredDelta']
        self._tkvar4.set(var if var != {} else '')

    def _cbCheckbutton(self, *args):
        self._config['adapterSettings'][self._currentAdapter]['changeOnRestart'] = self._tkvar2.get()

    def _cbExTime(self, *args):
        delta = self._tkvar4.get()
        if timeparse(delta) is None:
            return
        self._config['adapterSettings'][self._currentAdapter]['expiredDelta'] = delta

    def _cbReset(self, *args):
        self._config['adapterSettings'][self._currentAdapter] = vivdict()
        self._tkvar1.set(self._opts[0])
        self._mac.deleteMAC(self._currentAdapter)

    def _cbChange(self, *args):
        newMAC = self._mac.generateMAC(self._config['adapterSettings'][self._currentAdapter]['OUI'])
        self._mac.setMAC(self._currentAdapter, newMAC)

    def saveConfig(self, *args):
        with open('config.json', 'w') as jsonFile:
            dump(self._config, jsonFile)
        print('saved config')


if __name__ == '__main__':
    root = Tk()
    root.title("changeMAC - development version")
    root.geometry('400x150')
    App(root)
    root.mainloop()
