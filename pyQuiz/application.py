from ui.statusbar import StatusBar
from ui.dialog import InputDialog
from tkinter import *

class Application:
    def __init__(self, beforeShutdownCb = None):
        self.master = Tk()
        #self._username = self._usernamePrompt()
        self._fonts = {
            "question": ("Helvetica", 16),
            "answer": ("Helvetiva", 12)
        }
        self._initUiLayout()
        #self.master.geometry("{:d}x{:d}+{:d}+{:d}".format(450, 200, 20, 30))
        self.master.protocol("WM_DELETE_WINDOW", lambda: self._quit(beforeShutdownCb))

    def _usernamePrompt(self):
        dialog = InputDialog(self.master, "Enter a username")
        return dialog.result

    def _initUiLayout(self):
        self._qLabel = Label(self.master, text="Searching for players...", font=self._fonts["question"]) \
            .grid(row=0, columnspan=2, sticky=N+S)

        self._aLabelA = Button(self.master, text="A) ", anchor=W) \
            .grid(row=1, column=0, sticky=W+E, ipady=10)
        self._aLabelB = Button(self.master, text="B) ", anchor=W) \
            .grid(row=1, column=1, sticky=W+E, ipady=10)
        self._aLabelC = Button(self.master, text="C) ", anchor=W) \
            .grid(row=2, column=0, sticky=W+E, ipady=10)
        self._aLabelD = Button(self.master, text="D) ", anchor=W) \
            .grid(row=2, column=1, sticky=W+E, ipady=10)

        self._statusBar = StatusBar(self.master)
        self._statusBar.grid(row=3, columnspan=2, sticky=W+E)
        self._statusBar.set("Next question in %d seconds", 10)

        ## Grid configuration
        for col in range(2):
            Grid.columnconfigure(self.master, col, weight=1)
        Grid.rowconfigure(self.master, 0, weight=1)

    def _quit(self, beforeShutdownCb):
        if beforeShutdownCb is not None:
            beforeShutdownCb()
        self.master.destroy()

    def schedule(self, delayMs, fn, immediateExec=True):
        self.master.after(0 if immediateExec else delayMs, fn)
        self.master.after(0 if immediateExec else delayMs, lambda: self.schedule(delayMs, fn, False))

    def run(self):
        self.master.mainloop()
