#MenuTitle: Decompose all corner components and Overlap Shapes
# -*- coding: utf-8 -*-
# by Pedro Arilla, Diego Maldonado & DeepSeek


from __future__ import division, print_function, unicode_literals
from AppKit import NSString
import traceback
import time

__doc__="""
This Script uses Decomposes all components.py By Pedro Arilla to decompose corners, overlap shapes and Tidy up Paths
"""

Glyphs.clearLog()
print("Decompose all corner components @ " + time.strftime("%H:%M:%S"))

thisFont = Glyphs.font
for thisLayer in thisFont.selectedLayers:
	thisLayer.decomposeCorners()

print("All corner components decomposed.")

FlatGlyphs()

def tidy_paths():
    try:
        font = Glyphs.font
        if not font:
            print("❌ No font open!")
            return False
        
        for layer in font.selectedLayers:
            # Remove duplicate nodes and unnecessary points
            layer.cleanUpPaths()  
            
            print(f"✔ Tidied paths in {layer.parent.name}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

tidy_paths()