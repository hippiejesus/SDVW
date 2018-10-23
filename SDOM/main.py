#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import time

import qdarkstyle
import subprocess
import fader

import sqlaccess

from functions import *

import classes

def switch_screen(target):
    classes.dest.getScreen(target).show()
    
if __name__ == '__main__':
    # Initiate the main application
    app = classes.QtGui.QApplication(sys.argv)
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())
    
    # Instantiate the MainWindow
    main = classes.MainWindow()
    main.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())
    
    # Instantiate the Base workstation windows
    cr = classes.CR_Base()
    intake = classes.Intake_Base()
    extraction = classes.Extraction_Base()
    finishing = classes.Finishing_Base()
    yieldB = classes.Yield_Base()
    pm = classes.PM_Base()
    packaging = classes.Packaging_Base()
    pos = classes.POS_Base()
    
    # Add Base windows to destinations
    classes.dest.addScreen('cr',cr)
    classes.dest.addScreen('intake',intake)
    classes.dest.addScreen('extraction',extraction)
    classes.dest.addScreen('finishing',finishing)
    classes.dest.addScreen('yield',yieldB)
    classes.dest.addScreen('pm',pm)
    classes.dest.addScreen('packaging',packaging)
    classes.dest.addScreen('pos',pos)

    for i in classes.dest.screens.values():
        i.setWindowFlags(classes.QtCore.Qt.CustomizeWindowHint | classes.QtCore.Qt.WindowStaysOnTopHint)
    
    classes.dest.addScreen('MAIN',main)
    
    main.show()
    main.label.show()
    main.fadeInPix()
    
    sys.exit(app.exec_())
