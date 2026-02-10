# MenuTitle: Cheque as Métricas
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
import vanilla
import re
from GlyphsApp import Glyphs, Message

class MetricChecker(object):
	def __init__(self):
		self.w = vanilla.FloatingWindow((380, 520), "Cheque as métricas")
		
		padding = 15
		y = 15
		
		self.w.textScope = vanilla.TextBox((padding, y, -padding, 17), "Configurações", sizeStyle='small')
		y += 22
		self.w.allMasters = vanilla.CheckBox((padding, y, -padding, 20), "Checar todas as Masters", value=False, sizeStyle='small')
		y += 22
		self.w.useZones = vanilla.CheckBox((padding, y, -padding, 20), "Considerar Overshoot", value=True, sizeStyle='small')
		
		y += 30
		self.w.line1 = vanilla.HorizontalLine((padding, y, -padding, 1))
		y += 15
		
		self.w.textMetrics = vanilla.TextBox((padding, y, -padding, 17), "Considere (Font Info > Metrics):", sizeStyle='small')
		y += 25
		
		column_2 = 180 
		self.w.checkXHeight = vanilla.CheckBox((padding, y, column_2, 20), "Altura-x", value=True, sizeStyle='small')
		self.w.checkCapHeight = vanilla.CheckBox((column_2, y, -padding, 20), "Capitular", value=False, sizeStyle='small')
		y += 22
		self.w.checkAscender = vanilla.CheckBox((padding, y, column_2, 20), "Ascendente", value=True, sizeStyle='small')
		self.w.checkDescender = vanilla.CheckBox((column_2, y, -padding, 20), "Descendente", value=False, sizeStyle='small')
		y += 22
		self.w.checkSC = vanilla.CheckBox((padding, y, -padding, 20), "Small Caps", value=False, sizeStyle='small')
		
		y += 35
		self.w.runButton = vanilla.Button((padding, y, -padding, 30), "Cheque!", callback=self.process_script)
		
		y += 45
		self.w.line2 = vanilla.HorizontalLine((padding, y, -padding, 1))
		y += 15
		
		self.w.textResult = vanilla.TextBox((padding, y, -padding, 17), "Relatório:", sizeStyle='small')
		y += 22
		self.w.errorList = vanilla.TextEditor((padding, y, -padding, -padding), "", readOnly=True)
		
		self.w.open()

	def get_metric_id_by_type_or_name(self, font, target_type):
		"""Varre font.metrics de forma segura contra NoneTypes."""
		for m_info in font.metrics:
			# Verifica o tipo (propriedade interna do Glyphs)
			if m_info.type == target_type:
				return m_info.id
			
			# Verifica o nome de forma segura (previne o erro .lower() em None)
			m_name = m_info.name
			if m_name and m_name.lower() == target_type.lower():
				return m_info.id
		return None

	def get_zone_size(self, master, pos):
		for zone in master.alignmentZones:
			if int(zone.position) == int(pos):
				return abs(int(zone.size))
		return 0

	def is_valid_suffix(self, name):
		if "." not in name: return True
		suffix = name.split(".", 1)[1]
		if suffix in ["sc", "smcp", "alt"] or suffix.startswith("alt"):
			if suffix.startswith("alt"):
				rem = suffix[3:]
				return rem == "" or rem.isdigit()
			return True
		return bool(re.match(r"ss(0[1-9]|1[0-9]|2[0-4])$", suffix))

	def check_master(self, thisFont, thisMaster, doAsc, doXH, doDesc, doSC, doCap, useZones):
		# IDs das métricas
		sc_id = self.get_metric_id_by_type_or_name(thisFont, "Small Caps")
		cap_id = self.get_metric_id_by_type_or_name(thisFont, "Cap Height")
		
		# Coleta de valores
		m_vals = {
			"xh": thisMaster.xHeight,
			"cap": thisMaster.metricValues[cap_id].position if cap_id else thisMaster.capHeight,
			"asc": thisMaster.ascender,
			"desc": thisMaster.descender,
			"sc": thisMaster.metricValues[sc_id].position if sc_id else None
		}
		
		m_overs = {k: (self.get_zone_size(thisMaster, v) if (useZones and v is not None) else 0) for k, v in m_vals.items()}
		
		print("\n--- MASTER: %s ---" % thisMaster.name.upper())
		checks = {"xh": doXH, "cap": doCap, "asc": doAsc, "desc": doDesc, "sc": doSC}
		for k, active in checks.items():
			if active:
				val = m_vals[k] if m_vals[k] is not None else "NÃO DEFINIDO"
				ovr = "(Zone: %d)" % m_overs[k] if (useZones and m_vals[k] is not None) else ""
				print(" > %-10s : %s %s" % (k.upper(), val, ovr))

		asc_list = ["b", "d", "f", "h", "k", "l", "t", "thorn", "germandbls"]
		xh_list = ["a", "c", "e", "m", "n", "o", "r", "s", "u", "v", "w", "x", "z", "ae", "oe", "dotlessi", "dotlessj"]
		desc_list = ["g", "j", "p", "q", "y"]
		cap_list = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
		
		errors, ok, skip = [], [], []
		
		for glyph in thisFont.glyphs:
			name = glyph.name
			layer = glyph.layers[thisMaster.id]
			if glyph.category != "Letter" or not self.is_valid_suffix(name) or not (layer.paths or layer.components):
				skip.append(name)
				continue
			if any(c.component and c.component.category == "Mark" for c in layer.components):
				skip.append(name)
				continue
			
			base = name.split('.')[0]
			top = layer.bounds.origin.y + layer.bounds.size.height
			bottom = layer.bounds.origin.y
			is_sc = ".sc" in name or ".smcp" in name or glyph.category == "Smallcaps" or glyph.case == 3 

			processed = False
			if doSC and is_sc:
				ok.append(name)
				processed = True
				if m_vals["sc"] is not None:
					if abs(top - m_vals["sc"]) > (m_overs["sc"] if useZones else 1): errors.append(name)
				continue

			if not is_sc:
				if doCap and base in cap_list:
					ok.append(name)
					processed = True
					if abs(top - m_vals["cap"]) > (m_overs["cap"] if useZones else 1): errors.append(name)
				elif doAsc and base in asc_list:
					ok.append(name)
					processed = True
					if abs(top - m_vals["asc"]) > (m_overs["asc"] if useZones else 1): errors.append(name)
				elif doXH and base in xh_list:
					ok.append(name)
					processed = True
					if abs(top - m_vals["xh"]) > (m_overs["xh"] if useZones else 1): errors.append(name)

				if doDesc and base in desc_list:
					if name not in ok: ok.append(name)
					processed = True
					if abs(bottom - m_vals["desc"]) > (m_overs["desc"] if useZones else 1):
						if name not in errors: errors.append(name)
			
			if not processed: skip.append(name)
		
		print("\n✅ ANALISADOS (%d):\n%s" % (len(ok), ", ".join(sorted(ok)) if len(ok) < 10000 else "Muitos glifos para listar."))
		return sorted(list(set(errors))), sorted(ok)

	def process_script(self, sender):
		thisFont = Glyphs.font
		if not thisFont: return
		Glyphs.clearLog()
		self.w.errorList.set("") 
		
		masters = thisFont.masters if self.w.allMasters.get() else [thisFont.selectedFontMaster]
		
		# Validação SC
		if self.w.checkSC.get():
			if not self.get_metric_id_by_type_or_name(thisFont, "Small Caps"):
				Message("Métrica 'Small Caps' não encontrada no Font Info > Metrics.", title="Métrica em falta")
				return

		print("Relatório de métricas verticais\n" + "="*45)
		final_report = ""
		for m in masters:
			err, ok = self.check_master(thisFont, m, self.w.checkAscender.get(), self.w.checkXHeight.get(), self.w.checkDescender.get(), self.w.checkSC.get(), self.w.checkCapHeight.get(), self.w.useZones.get())
			if err:
				final_report += "🔴 %s\n%s\n\n" % (m.name.upper(), ", ".join(err))
				thisFont.newTab("/" + "/".join(err))
			else:
				final_report += "🟢 %s - OK (%d glifos)\n\n" % (m.name.upper(), len(ok))

		self.w.errorList.set(final_report if final_report else "Selecione uma métrica.")
		print("\n" + "="*45 + "\nValeu!")

MetricChecker()
