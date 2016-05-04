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
        self.master.wm_title("Quiz " + self.username)
        self._btnDefaultStyle = {
            "background": "#D9D9D9",
            "activebackground": "SpringGreen3",
            "font": ("Helvetica", 12),
        }
        self._btnPressedStyle = {
            "background": "forest green",
            "activebackground": "forest green",
            "font": ("Helvetica", 12, "bold"),
        }
        self._initUiLayout()
        self._btnPressCb = btnPressCb
        self.master.geometry("{:d}x{:d}+{:d}+{:d}".format(750, 300, 20, 30))
        self.master.protocol("WM_DELETE_WINDOW", lambda: self._quit(beforeShutdownCb))

    def _usernamePrompt(self):
        dialog = InputDialog(self.master, "Enter a username")
        return dialog.result

    def _initUiLayout(self):
        self._qLabel = Label(self.master, text="Searching for players...", font=("Helvetica", 16), wraplength=700)
        self._qLabel.grid(row=0, columnspan=2, sticky=W+E+N+S)

        self._buttons = {}

        self._btnA = Button(self.master, text="A) ", anchor=W, command=lambda: self._btnPressCb(self.BTN_A), **self._btnDefaultStyle)
        self._btnA.grid(row=1, column=0, sticky=W+E+N+S, ipady=10)
        self._buttons[self.BTN_A] = self._btnA

        self._btnB = Button(self.master, text="B) ", anchor=W, command=lambda: self._btnPressCb(self.BTN_B), **self._btnDefaultStyle)
        self._btnB.grid(row=1, column=1, sticky=W+E+N+S, ipady=10)
        self._buttons[self.BTN_B] = self._btnB

        self._btnC = Button(self.master, text="C) ", anchor=W, command=lambda: self._btnPressCb(self.BTN_C), **self._btnDefaultStyle)
        self._btnC.grid(row=2, column=0, sticky=W+E+N+S, ipady=10)
        self._buttons[self.BTN_C] = self._btnC

        self._btnD = Button(self.master, text="D) ", anchor=W, command=lambda: self._btnPressCb(self.BTN_D), **self._btnDefaultStyle)
        self._btnD.grid(row=2, column=1, sticky=W+E+N+S, ipady=10)
        self._buttons[self.BTN_D] = self._btnD

        self._scores = LabelFrame(self.master, text="Scores", padx=5, pady=5)
        self._scores.grid(row=3, columnspan=2, sticky=W+E)

        self._statusBar = StatusBar(self.master)
        self._statusBar.grid(row=4, columnspan=2, sticky=W+E)
        self._statusBar.set("Awaiting question...")

        ## Grid configuration
        for col in range(2):
            Grid.columnconfigure(self.master, col, weight=1)
        Grid.rowconfigure(self.master, 0, weight=1)

    def _setTimer(self, timeout_s):
        if int(timeout_s) > 0:
            self._statusBar.set("Next question in %d seconds", timeout_s)
            self.master.after(1000, lambda: self._setTimer(timeout_s - 1))
        else:
            self._statusBar.set("Awaiting question...")

    def _quit(self, beforeShutdownCb):
        if beforeShutdownCb is not None:
            beforeShutdownCb()
        self.master.destroy()

    def highlightBtn(self, btn_id):
        for k in self._buttons:
            if k == btn_id:
                self._buttons[k].config(**self._btnPressedStyle)
            else:
                self._buttons[k].config(**self._btnDefaultStyle)

    def updateQuestion(self, question):
        self._qLabel.config(text=question.getQuestion())
        self._btnA.config(text=question.getAnswerA(), **self._btnDefaultStyle)
        self._btnB.config(text=question.getAnswerB(), **self._btnDefaultStyle)
        self._btnC.config(text=question.getAnswerC(), **self._btnDefaultStyle)
        self._btnD.config(text=question.getAnswerD(), **self._btnDefaultStyle)
        self._setTimer(int(question.getTimeout()) / 1000)

    def updateScores(self, scores):
        for widget in self._scores.winfo_children():
            widget.destroy()

        row = 0
        for user in scores:
            Label(self._scores, text=user, justify=LEFT, anchor=W).grid(row=row, column=0, sticky=W+E)
            Label(self._scores, text=scores[user], justify=LEFT, anchor=W, font=("Helvetica", 10, "bold")).grid(row=row, column=1, padx=80)
            row += 1

    def schedule(self, delayMs, fn, immediateExec=True):
        self.master.after(0 if immediateExec else delayMs, fn)
        self.master.after(0 if immediateExec else delayMs, lambda: self.schedule(delayMs, fn, False))

    def run(self):
        self.master.mainloop()
