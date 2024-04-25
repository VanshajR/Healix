from tkinter import *
import customtkinter as cust


class TxtBox(cust.CTkTextbox):
    def __init__(self, parent, text, width, height, pad=30):
        super().__init__(parent, width=width, height=height)
        self.text = text
        self.width = width
        self.height = height
        self.pack(pady=pad)


class Button(cust.CTkButton):
    def __init__(self, parent, text, command, pad=30):
        super().__init__(parent)
        self.text = text
        self.command = command
        self.pack(pady=pad)


class Label(cust.CTkLabel):
    def __init__(self, parent, text, pad=30):
        super().__init__(parent)
        self.text = text
        self.pack(pady=pad)


class Entry(cust.CTkEntry):
    def __init__(self, parent, text, width, height, pad=30, radius=30):
        super().__init__(parent, width=width, height=height)
        self.placeholder_text = text
        self.corner_radius = radius
        self.width = width
        self.height = height
        self.pack(pady=pad)

    def clear(self):
        self.delete(0.0, "end")
