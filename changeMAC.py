# pylama:ignore=E501
from json import dump, load
from tkinter import Tk, Frame, StringVar, IntVar, OptionMenu, Label, Checkbutton, Button, Entry
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, OpenKey, QueryInfoKey, EnumKey, QueryValueEx

LOCAL_REGISTRY = ConnectRegistry(None, HKEY_LOCAL_MACHINE)


class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


# fix dict error
class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self._optionsdict = getNetworkAdapters(LOCAL_REGISTRY)
        try:
            with open('config.json', 'r') as jsonFile:
                self._config = Vividict(**load(jsonFile))
        except FileNotFoundError:
            self._config = Vividict()
        self._build()
        self._currentAdapter = self._optionsdict[self._tkvar1.get()]
        self._l1.bind('<Destroy>', self.saveConfig)

    def _build(self):
        self._l1 = Label(self.parent, text='Network interface')

        self._tkvar2 = IntVar(self.parent)
        self._tkvar2.trace('w', self._cbCheckbutton)
        cb1 = Checkbutton(self.parent, text='change MAC on restart', variable=self._tkvar2)

        b1 = Button(self.parent, text='change MAC')

        l2 = Label(self.parent, text='OUI')

        self._tkvar3 = StringVar(self.parent)
        self._tkvar3.trace('w', self._cbOUI)
        vcmd = (self.register(self._validateOUI), '%P', '%S')
        e1 = Entry(self.parent, textvariable=self._tkvar3, validate='key', vcmd=vcmd)

        self._tkvar1 = StringVar(self.parent)
        self._tkvar1.trace('w', self._cbDropdown)
        p1opts = tuple(self._optionsdict.keys())
        self._tkvar1.set(p1opts[0])
        p1 = OptionMenu(self.parent, self._tkvar1, *p1opts)

        self._l1.pack(side='top')
        p1.pack(side='top')
        l2.pack(side='top')
        e1.pack(side='top')
        cb1.pack(side='top')
        b1.pack(side='top')

    def _validateOUI(self, text, change):
        if(change in '0123456789ABCDEF' and len(text) < 7):
            return True
        self.bell()
        return False

    def _cbOUI(self, *args):
        text = self._tkvar3.get()
        if(len(text) == 6):
            self._config['adapterSettings'][self._currentAdapter]['OUI'] = text[0:6]
            print(self._config)

    def _cbDropdown(self, *args):
        print(f'type: {type(self._config).__name__}')
        self._currentAdapter = self._optionsdict[self._tkvar1.get()]
        try:
            var = self._config['adapterSettings'][self._currentAdapter]['changeOnRestart']
            self._tkvar2.set(var if var != {} else 0)
        except Exception:
            self._tkvar2.set(0)
        try:
            var = self._config['adapterSettings'][self._currentAdapter]['OUI']
            self._tkvar3.set(var if var != {} else '')
        except Exception:
            self._tkvar3.set('')
        print(self._optionsdict[self._tkvar1.get()])

    def _cbCheckbutton(self, *args):
        self._config['adapterSettings'][self._currentAdapter]['changeOnRestart'] = self._tkvar2.get()
        print(self._config)

    def saveConfig(self, *args):
        with open('config.json', 'w') as jsonFile:
            dump(self._config, jsonFile)
        print('saved config')


# get available network adapters
def getNetworkAdapters(registry):
    adaptersKey = OpenKey(registry, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}")
    adapters = {}
    for i in range(QueryInfoKey(adaptersKey)[0]):
        try:
            subKeyString = EnumKey(adaptersKey, i)
            subKey = OpenKey(adaptersKey, subKeyString)
            type = QueryValueEx(subKey, '*PhysicalMediaType')[0]
            if type == 14:  # if network adapter
                try:
                    QueryValueEx(subKey, 'NoDisplayClass')
                except(Exception):
                    adapters[QueryValueEx(subKey, 'DriverDesc')[0]] = subKeyString
        except Exception:
            break
    return adapters


root = Tk()
root.title("changeMAC - development version")
root.geometry('400x400')
App(root)
root.mainloop()
