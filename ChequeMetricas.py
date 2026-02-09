# MenuTitle: Cheque a Métrica
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
import vanilla

class MetricChecker(object):
	def __init__(self):
		# Janela mais enxuta e organizada
		self.w = vanilla.FloatingWindow((380, 520), "Cheque a Métrica")
		
		padding = 15
		y = 15
		
		# --- SEÇÃO: CONFIGURAÇÕES ---
		self.w.textScope = vanilla.TextBox((padding, y, -padding, 17), "Configurações", sizeStyle='small')
		y += 22
		self.w.allMasters = vanilla.CheckBox((padding, y, -padding, 20), "Checar todas as Masters (senão apenas a selecionada)", value=False, sizeStyle='small')
		y += 22
		self.w.useZones = vanilla.CheckBox((padding, y, -padding, 20), "Considerar Overshoot", value=True, sizeStyle='small')
		
		y += 30
		self.w.line1 = vanilla.HorizontalLine((padding, y, -padding, 1))
		y += 15
		
		# --- SEÇÃO: O QUE CHECAR ---
		self.w.textMetrics = vanilla.TextBox((padding, y, -padding, 17), "Considere:", sizeStyle='small')
		y += 25
		
		column_2 = 180 # Posição da segunda coluna de checkboxes
		
		self.w.checkXHeight = vanilla.CheckBox((padding, y, column_2, 20), "Altura-x", value=True, sizeStyle='small')
		self.w.checkCapHeight = vanilla.CheckBox((column_2, y, -padding, 20), "Capitular", value=False, sizeStyle='small')
		y += 22
		self.w.checkAscender = vanilla.CheckBox((padding, y, column_2, 20), "Ascendente", value=True, sizeStyle='small')
		self.w.checkDescender = vanilla.CheckBox((column_2, y, -padding, 20), "Descendente", value=False, sizeStyle='small')
		y += 22
		self.w.checkSC = vanilla.CheckBox((padding, y, -padding, 20), "Small Caps", value=False, sizeStyle='small')
		
		y += 35
		self.w.runButton = vanilla.Button((padding, y, -padding, 30), "Analise!", callback=self.process_script)
		
		y += 45
		self.w.line2 = vanilla.HorizontalLine((padding, y, -padding, 1))
		y += 15
		
		self.w.textResult = vanilla.TextBox((padding, y, -padding, 17), "Relatório:", sizeStyle='small')
		y += 22
		self.w.errorList = vanilla.TextEditor((padding, y, -padding, -padding), "", readOnly=True)
		
		self.w.open()

	def get_zone_size(self, master, pos):
		for zone in master.alignmentZones:
			if int(zone.position) == int(pos):
				return abs(int(zone.size))
		return 0

	def get_metric_height(self, master, metric_name):
		# Fallback para parâmetros customizados ou métricas G3
		param = master.customParameters[metric_name]
		if param: return int(param)
		
		# Mapeamento de tipos para Glyphs 3
		metric_map = {
			"smallCapHeight": GSMetricTypeSmallcaps,
			"capHeight": GSMetricTypeCapHeight
		}
		
		if hasattr(master, "metrics"):
			for metric in master.metrics:
				try:
					if metric.type() == metric_map.get(metric_name):
						return int(metric.position())
				except: continue
		return None

	def check_master(self, thisFont, thisMaster, doAsc, doXH, doDesc, doSC, doCap, useZones):
		# Valores de referência
		ascVal = thisMaster.ascender
		xhVal = thisMaster.xHeight
		descVal = thisMaster.descender
		capVal = thisMaster.capHeight
		scVal = self.get_metric_height(thisMaster, "smallCapHeight")
		
		# Listas estritas de Letras Base
		asc_list = ["b", "d", "f", "h", "k", "l", "t", "thorn", "germandbls"]
		xh_list = ["a", "c", "e", "m", "n", "o", "r", "s", "u", "v", "w", "x", "z", "ae", "oe", "dotlessi", "dotlessj"]
		desc_list = ["g", "j", "p", "q", "y"]
		cap_list = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split()
		
		# Overshoots das Zonas
		o_asc = self.get_zone_size(thisMaster, ascVal) if useZones else 1
		o_xh = self.get_zone_size(thisMaster, xhVal) if useZones else 1
		o_desc = self.get_zone_size(thisMaster, descVal) if useZones else 1
		o_cap = self.get_zone_size(thisMaster, capVal) if useZones else 1
		o_sc = self.get_zone_size(thisMaster, scVal) if (useZones and scVal) else 1
		
		errors = []
		
		for glyph in thisFont.glyphs:
			if glyph.category != "Letter": continue
			layer = glyph.layers[thisMaster.id]
			if not layer.paths and not layer.components: continue
			if any(c.component.category == "Mark" for c in layer.components): continue
			
			name = glyph.name
			base = name.split('.')[0]
			top = layer.bounds.origin.y + layer.bounds.size.height
			bottom = layer.bounds.origin.y

			# 1. SMALL CAPS
			if doSC and glyph.case == GSSmallcaps:
				if scVal and (top > (scVal + o_sc + 1) or top < (scVal - 1)): errors.append(name)
				continue

			# 2. MAIÚSCULAS (Cap Height)
			if doCap and base in cap_list:
				if top > (capVal + o_cap + 1) or top < (capVal - 1): errors.append(name)
				continue

			# 3. ASCENDENTES
			if doAsc and base in asc_list and glyph.case != GSSmallcaps:
				if top > (ascVal + o_asc + 1) or top < (ascVal - 1): errors.append(name)
			
			# 4. X-HEIGHT
			elif doXH and base in xh_list and glyph.case != GSSmallcaps:
				if top > (xhVal + o_xh + 1) or top < (xhVal - 1): errors.append(name)

			# 5. DESCENDENTES (Checa a base)
			if doDesc and base in desc_list and glyph.case != GSSmallcaps:
				if bottom < (descVal - o_desc - 1) or bottom > (descVal + 1): errors.append(name)
		
		return sorted(list(set(errors)))

	def process_script(self, sender):
		thisFont = Glyphs.font
		if not thisFont: return
		
		masters_to_check = thisFont.masters if self.w.allMasters.get() else [thisFont.selectedFontMaster]
		report = ""
		
		for m in masters_to_check:
			err = self.check_master(thisFont, m, self.w.checkAscender.get(), self.w.checkXHeight.get(), self.w.checkDescender.get(), self.w.checkSC.get(), self.w.checkCapHeight.get(), self.w.useZones.get())
			if err:
				report += "🔴 %s\n%s\n\n" % (m.name.upper(), ", ".join(err))
				thisFont.newTab("/" + "/".join(err))
			else:
				report += "🟢 %s - OK!\n\n" % m.name.upper()

		self.w.errorList.set(report if report else "Selecione uma métrica.")

MetricChecker()