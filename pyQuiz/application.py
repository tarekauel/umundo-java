import random

from ui.statusbar import StatusBar
from ui.dialog import InputDialog
from tkinter import *

class Application:
    BTN_A = "A"
    BTN_B = "B"
    BTN_C = "C"
    BTN_D = "D"

    def __init__(self, btnPressCb, beforeShutdownCb = None):
        self.master = Tk()
        #self.username = self._usernamePrompt()
        self.username = "Python client" + str(random.randint(1, 10000))
        self._fonts = {
            "question": ("Helvetica", 12),
            "answer": ("Helvetiva", 12)
        }
        self._initUiLayout()
        self._btnPressCb = btnPressCb
        #self.master.geometry("{:d}x{:d}+{:d}+{:d}".format(450, 200, 20, 30))
        self.master.protocol("WM_DELETE_WINDOW", lambda: self._quit(beforeShutdownCb))

    def _usernamePrompt(self):
        dialog = InputDialog(self.master, "Enter a username")
        return dialog.result

    def _initUiLayout(self):
        self._qLabel = Label(self.master, text="Searching for players...", font=self._fonts["question"])
        self._qLabel.grid(row=0, columnspan=2, sticky=N+S)

        self._btnA = Button(self.master, text="A) ", anchor=W, command=lambda: self._btnPressCb(self.BTN_A))
        self._btnA.grid(row=1, column=0, sticky=W+E, ipady=10)

        self._btnB = Button(self.master, text="B) ", anchor=W, command=lambda: self._btnPressCb(self.BTN_B))
        self._btnB.grid(row=1, column=1, sticky=W+E, ipady=10)

        self._btnC = Button(self.master, text="C) ", anchor=W, command=lambda: self._btnPressCb(self.BTN_C))
        self._btnC.grid(row=2, column=0, sticky=W+E, ipady=10)

        self._btnD = Button(self.master, text="D) ", anchor=W, command=lambda: self._btnPressCb(self.BTN_D))
        self._btnD.grid(row=2, column=1, sticky=W+E, ipady=10)

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

    def updateQuestion(self, question):
        self._qLabel.config(text=question.getQuestion())
        self._btnA.config(text=question.getAnswerA())
        self._btnB.config(text=question.getAnswerB())
        self._btnC.config(text=question.getAnswerC())
        self._btnD.config(text=question.getAnswerD())
        self._statusBar.set("Next question in %d seconds", int(question.getTimeout()) / 10000)

    def schedule(self, delayMs, fn, immediateExec=True):
        self.master.after(0 if immediateExec else delayMs, fn)
        self.master.after(0 if immediateExec else delayMs, lambda: self.schedule(delayMs, fn, False))

    def run(self):
        self.master.mainloop()
