#MenuTitle: Export Sbix Color Font
# -*- coding: utf-8 -*-

__doc__="""

(GUI) This script is set to export a font without overlap, 
no autohint and TTF flavored, the best way to export an sbix color font

The default folder is configured to ~/Desktop.

"""

from os.path import expanduser

home = os.path.expanduser("~")
exportFolder = home + "Desktop"

for instance in Glyphs.font.instances:
        instance.generate('TTF', FontPath = exportFolder, AutoHint = False, RemoveOverlap = False)

Glyphs.showNotification('Export fonts', 'The export of %s was successful.' % (Glyphs.font.familyName))
