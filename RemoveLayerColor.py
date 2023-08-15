#MenuTitle: Remove Layer Color in all masters
# -*- coding: utf-8 -*-
__doc__ = """

Removes layer color in all masters from the selected glyph.

"""

# This Script was generated with Bard - https://bard.google.com/

def remove_layer_color(glyph):
  """Removes layer color in all masters from the selected glyph."""
  for master in glyph.font.masters:
    for layer in glyph.layers:
      if layer.master == master:
        layer.color = None

# Get the selected glyph.
glyph = Glyphs.font.selection[0]

# Run the script.
remove_layer_color(glyph)
