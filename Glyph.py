#!/usr/bin/env python
"""
Glyph.py
Copyright (c) 2015, Aaron Pop
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import Tkinter 
import tkMessageBox 

class Glyph():
    #
    # Initilization function for the Glyph class
    #
    def __init__(self):
        # Variable for showing the "ruler" to false
        self.ViewOffsets = False

        # Variable used to track the width and height of a character
        #  Narrow = 8 bits
        #  Wide = 16 bits
        self.charwidth = 8
        self.charheight = 19

        # Variable for tracking the margin size (both Vertical and Horizontal) of the canvas
        # attempting to draw outside of this margin will not be rendered on the canvas
        self.margins = 2

        # Variable for tracking this Tk Widget's root widget
        self.root = Tkinter.Tk()

        # Set the Title bar of the widget
        self.root.title("UEFI Glyph Creator")

        # Calculate the height/width of each square in a glyph
        #  if the resolution is low, then set a minimum of 20
        self.smallestsquare = self.root.winfo_screenheight()/70
        if self.smallestsquare < 20:
            self.smallestsquare = 20

        # Set the current square size based on the smallest square
        self.square = self.smallestsquare

        # Create a Menu, and configure the root widget to use it
        menubar = Tkinter.Menu(self.root, tearoff=0)
        self.root.config(menu=menubar)
        
        # Add an Edit Menu to the menu bar
        EditMenu = Tkinter.Menu(menubar, tearoff=0)
        EditMenu.add_command(label="Increase Size", command=self.IncreaseSize)
        EditMenu.add_command(label="Decrease Size", command=self.DecreaseSize)
        EditMenu.add_checkbutton(label="Show Offsets", variable=self.ViewOffsets, command=self.SwitchShowOffsets)
        EditMenu.add_command(label="Clear", command=self.Clear)
        menubar.add_cascade(label="Edit", menu=EditMenu)    

        # Add an Options menu to the menu bar
        OptionsMenu = Tkinter.Menu(menubar, tearoff=0) 
        OptionsMenu.add_checkbutton(label="WideChar", variable=self.charwidth, command=self.SwitchToWideChar)
        OptionsMenu.add_command(label="Copy To Clipboard", command=self.CopyBufferToClipBoard)
        OptionsMenu.add_command(label="Import from ClipBoard", command=self.ImportClipBoardToBuffer)
        menubar.add_cascade(label="Options", menu=OptionsMenu)    

        # Add a Help menu to the menu bar
        HelpMenu = Tkinter.Menu(menubar, tearoff=0)
        HelpMenu.add_command(label="About", command=self.About)
        menubar.add_cascade(label="Help", menu=HelpMenu)    

        # Create a Canvas widget and add it to the root Widget
        self.canvas = Tkinter.Canvas(self.root, bg="white")
        self.canvas.pack(side = Tkinter.TOP, fill=Tkinter.BOTH, expand=1)

        # Bind the left mouse button click to function Clicked
        self.root.bind('<Button-1>', self.Clicked)

        # Bind keypad + and the plus keys to the IncreaseSize function
        self.root.bind('<KP_Add>', self.IncreaseSize)
        self.root.bind('<plus>', self.IncreaseSize)

        # Bind keypad - and the minus keys to the DecreaseSize function
        self.root.bind('<KP_Subtract>', self.DecreaseSize)
        self.root.bind('<minus>', self.DecreaseSize)

        # Initialize the Canvas area with the Glyph Information
        self.InitializeCanvas()

        # Create a status bar that show the current Width and Height
        self.StatusBar = Tkinter.Label(self.root, text="", bd=1, relief=Tkinter.GROOVE, anchor=Tkinter.W)
        self.StatusBar.config(text="Width = %d Height = %d  " %( self.charwidth, self.charheight))
        self.StatusBar.pack(side=Tkinter.TOP, fill=Tkinter.X)

        # Start the Widget
        self.root.mainloop()

    #
    # Determine the current height requirements for the canvas area
    #
    def CurrentHeight(self):
        retval = self.charheight * self.square + self.margins*2
        if self.ViewOffsets:
            retval = retval + self.square
        return retval

    #
    # Determine the current width requirements for the canvas area
    #
    def CurrentWidth(self):
        retval = self.charwidth * self.square + self.margins*2
        if self.ViewOffsets:
            retval = retval + self.square
        return retval

    #
    # Display a About this application popup box
    #
    def About(self):
        tkMessageBox.showinfo("About this application...", "Python application to allow Glyph creation for both Wide Characters and Narrow Characters.")

    #
    # Increase the size of the canvas area
    #
    def IncreaseSize(self, event=None):
        array = self.CurrentToArray()
        self.square = self.square+2
        self.InitializeCanvas(array)    

    #
    # Decrease the size of the canvas area
    #
    def DecreaseSize(self, event=None):
         if self.square > self.smallestsquare:
            array = self.CurrentToArray()
            self.square = self.square-2
            self.InitializeCanvas(array)

    #
    # Switch on or off the numbers for the squares
    #
    def SwitchShowOffsets(self):
        array = self.CurrentToArray()
        self.ViewOffsets = not self.ViewOffsets
        self.InitializeCanvas(array)

    #
    # Clear the currently screen
    #
    def Clear(self):
        for y in range(0, self.charheight):
            for x in range(0, self.charwidth):
                if self.ViewOffsets:
                    cid = self.canvas.find_closest((x+1)*self.square+self.margins,(y+1)*self.square+self.margins)
                else:
                    cid = self.canvas.find_closest(x*self.square+self.margins,y*self.square+self.margins)
                self.canvas.itemconfigure(cid[0], fill="white")

    #
    # Copy the current set of settings into an array
    #
    def CurrentToArray(self):
        finalarray = []
        for y in range(0, self.charheight):
            currentarray = []
            for x in range(0, self.charwidth):
                if self.ViewOffsets:
                    cid = self.canvas.find_closest((x+1)*self.square+self.margins,(y+1)*self.square+self.margins)
                else:
                    cid = self.canvas.find_closest(x*self.square+self.margins,y*self.square+self.margins)
                if len(cid) > 0:
                    if self.canvas.itemcget(cid[0], "fill") == "black":
                        currentarray.append(1)
                    else:
                        currentarray.append(0)
            finalarray.append(currentarray)
        return finalarray

    #
    # Show the ruler
    #
    def ShowRuler(self):
        if self.ViewOffsets:
            for j in range(0, self.charheight):
                self.canvas.create_text(self.margins+.5*self.square, self.margins+(j+1)*self.square+.5*self.square, text="%d"%(j))
            for i in range(0, self.charwidth):
                self.canvas.create_text(self.margins+(i+1)*self.square + .5*self.square, self.margins+.5*self.square, text="%d"%(i))

    #
    # If an array is passed to current, use the array to draw the canvas area with current settings
    #  otherwise delete all the current canvas area and redraw
    #
    def InitializeCanvas(self, current=None):
        self.canvas.delete("all")
        self.canvas.config(width=self.CurrentWidth(), height=self.CurrentHeight())
        self.ShowRuler()

        for j in range(0, self.charheight):
            for i in range(0, self.charwidth):
                fillit = "white"
                margincorrection = self.margins

                if self.ViewOffsets:
                    margincorrection = margincorrection + self.square

                if current != None and len(current[0]) > i:
                    if current[j][i] == 1:
                        fillit = "black"
                rect = self.canvas.create_rectangle(i*self.square+margincorrection, j*self.square+margincorrection, (i+1)*self.square+margincorrection, (j+1)*self.square+margincorrection, fill=fillit)

        self.root.update_idletasks()
        if self.root.winfo_width() < self.root.winfo_reqwidth() or self.root.winfo_height() < self.root.winfo_reqheight():
            self.root.winfo_toplevel().wm_geometry("")

    #
    # Switch from a narrow character to a wide character area
    #
    def SwitchToWideChar(self):
        array = self.CurrentToArray()
        if self.charwidth == 8:
            self.charwidth = 16
        else:
            self.charwidth = 8
        self.StatusBar.config(text="Width = %d Height = %d  " %( self.charwidth, self.charheight))
        self.InitializeCanvas(array)

    #
    # Copy the current settings to the clipboard area
    #
    def CopyBufferToClipBoard(self):
        finalstring = ""
        for y in range(0, self.charheight):
            if y > 0:
                finalstring += ","
            currentbyte = ""
            for x in range(0, 8):
                if self.ViewOffsets:
                    cid = self.canvas.find_closest((x+1)*self.square+self.margins,(y+1)*self.square+self.margins)
                else:
                    cid = self.canvas.find_closest(x*self.square+self.margins,y*self.square+self.margins)
                if len(cid) > 0:
                    if self.canvas.itemcget(cid[0], "fill") == "black":
                        currentbyte += "1"
                    else:
                        currentbyte += "0"
            finalstring += "{%s}" % (hex( int(currentbyte, 2)))
        if self.charwidth > 8:
            finalstring += "\n"
            for y in range(0, self.charheight):
                if y > 0:
                    finalstring += ","
                currentbyte = ""
                for x in range(8, 16):
                    if self.ViewOffsets:
                        cid = self.canvas.find_closest((x+1)*self.square+self.margins,(y+1)*self.square+self.margins)
                    else:
                        cid = self.canvas.find_closest(x*self.square+self.margins,y*self.square+self.margins)
                    if len(cid) > 0:
                        if self.canvas.itemcget(cid[0], "fill") == "black":
                            currentbyte += "1"
                        else:
                            currentbyte += "0"
                finalstring += "{%s}" % (hex( int(currentbyte, 2)))
        self.root.clipboard_clear()
        self.root.clipboard_append(finalstring)

    #
    # Attempt to import from the clipboard area and put the information into the canvas area
    #
    def ImportClipBoardToBuffer(self):
        buffer = self.root.clipboard_get()
        try:
            buffer = buffer.replace('{', "")
            buffer = buffer.replace('}', "")
            buffer = buffer.split(",")
            RetBuf = []
            for value in buffer:
                RetBuf.append( [int(value,16) >> i & 1 for i in range(self.charwidth-1,-1,-1)] )
            self.InitializeCanvas(RetBuf)
        except:
            tkMessageBox.showinfo("Import Error", "Error Importing from the clipboard")
            print "Error on buffer"

    #
    # Using the mouse click event information (x, y) find the closest item and if that item is 
    #  a rectangle, then toggle the rectangle's color (white->black, black->white)
    #
    def Clicked(self, event):
        cid = self.canvas.find_closest(event.x,event.y)
        if len(cid) > 0:
            if self.canvas.type(cid[0]) == "rectangle":
                if self.canvas.itemcget(cid[0], "fill") == "black":
                    self.canvas.itemconfigure(cid[0], fill="white")
                else:
                    self.canvas.itemconfigure(cid[0], fill="black")


def main():
    glyph = Glyph()

if __name__ == '__main__':
    main() 