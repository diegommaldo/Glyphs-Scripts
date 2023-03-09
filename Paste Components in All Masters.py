#MenuTitle: Paste Components in All Masters
# -*- coding: utf-8 -*-
__doc__="""
This script pastes components in all masters.
"""

import GlyphsApp

def main():
    font = Glyphs.font
    selectedLayer = font.selectedLayers[0]
    selectedGlyph = selectedLayer.parent
    selectedComponents = selectedLayer.components
    
    for master in font.masters:
        if master != font.selectedFontMaster:
            newLayer = selectedGlyph.layers[master.id]
            for component in selectedComponents:
                newLayer.components.append(component.copy())
    
    font.enableUpdateInterface()

if __name__ == '__main__':
    main()