# MenuTitle: Controle de Projeto
# -*- coding: utf-8 -*-
__doc__ = """
Abre janela avançada de notas para 
desenvolvimento de projeto.
"""

import datetime
import vanilla
from AppKit import (
    NSPasteboard, NSStringPboardType, NSAlert, NSImage, NSSize, 
    NSBezierPath, NSColor, NSRect, NSImageCell, NSSortDescriptor
)
from GlyphsApp import Glyphs


class ReviewNotesFloatingWindow(object):
    def __init__(self):
        Glyphs.clearLog()

        self._updating_obs = True
        self._color_image_cache = {}

        self.status_cycles = {
            "🔴": "🟡",
            "🟡": "🟢",
            "🟢": "🔴"
        }

        self.masters_list = self.get_master_names()
        self.groups_list = self.get_available_groups()
        self.status_filters = ["Todos Status", "🔴 Pendentes", "🟡 Em Processo", "🟢 Concluídos"]
        self.axes_filters = self.get_available_axes_filters()
        
        # Opções simplificadas de ajuste e filtro
        self.kerning_adjust_options = ["+", "-", "?"]
        self.kerning_adjust_filters = ["Todos Ajustes", "+ Aumentar", "- Diminuir", "? Verificar"]

        self.w = vanilla.FloatingWindow((760, 680), "Controle de Projeto 1.1", minSize=(550, 490))

        file_name = self.get_current_file_name()
        self.w.fileHeaderLabel = vanilla.TextBox((12, 12, -12, 18), f"Arquivo: {file_name}", sizeStyle="small")
        self.w.fileHeaderLabel.getNSTextField().setTextColor_(self.get_secondary_color())

        # Ajustado para dar folga no topo do container das abas
        self.w.tabs = vanilla.Tabs((12, 38, -12, -72), ["Glifos", "Kerning", "Tarefas"], callback=self.on_tab_changed)
        glyphsTab = self.w.tabs[0]
        kerningTab = self.w.tabs[1]
        tasksTab = self.w.tabs[2]

        # ==================== ABA "GLIFOS" ====================
        glyphsTab.topMasterLabel = vanilla.TextBox((0, 10, 50, 17), "Master:", sizeStyle="small")
        glyphsTab.topMasterSelect = vanilla.PopUpButton((52, 6, 110, 22), self.masters_list, callback=self.on_filter_changed)
        glyphsTab.manualGlyphInput = vanilla.EditText((170, 6, 190, 22), "", placeholder="ex: a, b, c")
        glyphsTab.addBtn = vanilla.Button((366, 6, 32, 22), "➕", callback=self.add_glyphs_action)
        glyphsTab.allMastersCheck = vanilla.CheckBox((408, 8, 115, 18), "Todas masters", sizeStyle="small", value=False)

        # Filtro de Grupo + Atribuição de Grupo em Lote
        glyphsTab.groupFilterLabel = vanilla.TextBox((0, 42, 50, 17), "Grupo:", sizeStyle="small")
        glyphsTab.groupFilterSelect = vanilla.PopUpButton((52, 38, 120, 22), self.groups_list, callback=self.on_filter_changed)
        glyphsTab.assignGroupInput = vanilla.EditText((178, 38, 140, 22), "", placeholder="Novo/Definir grupo")
        glyphsTab.assignGroupBtn = vanilla.Button((324, 38, 36, 22), "📁+", sizeStyle="small", callback=self.assign_group_to_selected)

        # Status + Busca por texto
        glyphsTab.statusFilterLabel = vanilla.TextBox((0, 74, 50, 17), "Status:", sizeStyle="small")
        glyphsTab.statusFilterSelect = vanilla.PopUpButton((52, 70, 120, 22), self.status_filters, callback=self.on_filter_changed)
        glyphsTab.searchInput = vanilla.EditText((178, 70, -0, 22), "", placeholder="🔍 Buscar glifo, grupo ou obs...", callback=self.on_filter_changed)

        # Linha do Eixo + Botão "Update Cor"
        glyphsTab.axisFilterLabel = vanilla.TextBox((0, 106, 50, 17), "Eixo:", sizeStyle="small")
        glyphsTab.axisFilterSelect = vanilla.PopUpButton((52, 102, 180, 22), self.axes_filters, callback=self.on_filter_changed)
        glyphsTab.refreshBtn = vanilla.Button((-92, 102, 85, 22), "Update Cor", sizeStyle="small", callback=self.manual_refresh_action)

        glyphsTab.counterBox = vanilla.Box((0, 134, -0, 26))
        glyphsTab.counterText = vanilla.TextBox((8, 138, -118, 18), "Resumo: 🔴 0  |  🟡 0  |  🟢 0  (Total: 0)", sizeStyle="small")
        glyphsTab.filterRedBtn = vanilla.Button((-112, 136, 22, 18), "🔴", sizeStyle="small", callback=lambda s: self.set_status_filter(1))
        glyphsTab.filterYellowBtn = vanilla.Button((-88, 136, 22, 18), "🟡", sizeStyle="small", callback=lambda s: self.set_status_filter(2))
        glyphsTab.filterGreenBtn = vanilla.Button((-64, 136, 22, 18), "🟢", sizeStyle="small", callback=lambda s: self.set_status_filter(3))
        glyphsTab.removeGlyphBtn = vanilla.Button((-38, 135, 30, 20), "➖", sizeStyle="small", callback=self.delete_selected_glyph_rows)

        glyphsTab.topLine = vanilla.HorizontalLine((0, 168, -0, 1))

        table_masters = [m for m in self.masters_list if m != "Todas"]
        columnDescriptions = [
            {"title": "", "key": "status", "width": 28, "minWidth": 24, "maxWidth": 40},
            {"title": "Grupo", "key": "group", "width": 100, "minWidth": 80, "maxWidth": 200, "editable": True},
            {"title": "Master", "key": "master", "width": 100, "minWidth": 90, "maxWidth": 200, "editable": True, "editCellData": {"type": "popUpButton", "items": table_masters}},
            {"title": "Glifo", "key": "glyph", "width": 80, "minWidth": 60, "maxWidth": 180},
            {"title": "Cor", "key": "colorIcon", "width": 32, "minWidth": 32, "maxWidth": 40},
            {"title": "Observações", "key": "obs", "width": 250, "minWidth": 100, "maxWidth": 1000, "editable": True}
        ]
        
        glyphsTab.list = vanilla.List((0, 176, -0, -0), [],
                                     columnDescriptions=columnDescriptions,
                                     doubleClickCallback=self.on_double_click_row,
                                     editCallback=self.on_edit_obs_direct,
                                     allowsMultipleSelection=True,
                                     allowsSorting=True)
        
        table_view = glyphsTab.list.getNSTableView()
        table_view.setRowHeight_(22)
        table_view.setAllowsMultipleSelection_(True)

        color_column = table_view.tableColumnWithIdentifier_("colorIcon")
        if color_column:
            image_cell = NSImageCell.alloc().init()
            color_column.setDataCell_(image_cell)
            color_descriptor = NSSortDescriptor.sortDescriptorWithKey_ascending_("_colorSort", True)
            color_column.setSortDescriptorPrototype_(color_descriptor)

        self.topMasterSelect = glyphsTab.topMasterSelect
        self.allMastersCheck = glyphsTab.allMastersCheck
        self.manualGlyphInput = glyphsTab.manualGlyphInput
        self.groupFilterSelect = glyphsTab.groupFilterSelect
        self.assignGroupInput = glyphsTab.assignGroupInput
        self.statusFilterSelect = glyphsTab.statusFilterSelect
        self.searchInput = glyphsTab.searchInput
        self.axisFilterSelect = glyphsTab.axisFilterSelect
        self.counterText = glyphsTab.counterText
        self.list = glyphsTab.list

        # ==================== ABA "KERNING" ====================
        kerning_masters = [m for m in self.masters_list if m != "Todas"]
        
        # Rótulo da área de inserção
        kerningTab.insertHeaderLabel = vanilla.TextBox((0, 6, 200, 17), "Insira Pares de Glifos:", sizeStyle="small")

        # Linha 1: Inputs ajustados verticalmente (y=26)
        kerningTab.masterSelect = vanilla.PopUpButton((0, 26, 105, 22), kerning_masters)
        kerningTab.leftInput = vanilla.EditText((112, 26, 55, 22), "", placeholder="A")
        kerningTab.rightInput = vanilla.EditText((173, 26, 55, 22), "", placeholder="V")
        kerningTab.adjustSelect = vanilla.PopUpButton((234, 26, 50, 22), self.kerning_adjust_options)
        kerningTab.noteInput = vanilla.EditText((290, 26, -75, 22), "", placeholder="Observação")
        
        # Botões da linha de entrada
        kerningTab.removeKernBtn = vanilla.Button((-68, 26, 30, 22), "➖", sizeStyle="small", callback=self.delete_selected_kerning_rows)
        kerningTab.addKernBtn = vanilla.Button((-34, 26, 30, 22), "➕", callback=self.add_kerning_action)

        # Linha 2: Filtros (y=58)
        kerningTab.statusFilterLabel = vanilla.TextBox((0, 62, 45, 17), "Status:", sizeStyle="small")
        kerningTab.statusFilterSelect = vanilla.PopUpButton((48, 58, 120, 22), self.status_filters, callback=self.on_kerning_filter_changed)
        
        kerningTab.adjustFilterLabel = vanilla.TextBox((178, 62, 45, 17), "Ajuste:", sizeStyle="small")
        kerningTab.adjustFilterSelect = vanilla.PopUpButton((225, 58, 120, 22), self.kerning_adjust_filters, callback=self.on_kerning_filter_changed)

        # Linha 3: Resumo (y=88)
        kerningTab.counterBox = vanilla.Box((0, 88, -0, 26))
        kerningTab.counterText = vanilla.TextBox((8, 92, -95, 18), "Resumo: 🔴 0  |  🟡 0  |  🟢 0  (Total: 0)", sizeStyle="small")
        kerningTab.filterRedBtn = vanilla.Button((-88, 90, 22, 18), "🔴", sizeStyle="small", callback=lambda s: self.set_kerning_status_filter(1))
        kerningTab.filterYellowBtn = vanilla.Button((-64, 90, 22, 18), "🟡", sizeStyle="small", callback=lambda s: self.set_kerning_status_filter(2))
        kerningTab.filterGreenBtn = vanilla.Button((-40, 90, 22, 18), "🟢", sizeStyle="small", callback=lambda s: self.set_kerning_status_filter(3))

        kerningTab.topLine = vanilla.HorizontalLine((0, 122, -0, 1))

        kerningColumns = [
            {"title": "", "key": "status", "width": 28, "minWidth": 24, "maxWidth": 40},
            {"title": "Master", "key": "master", "width": 120, "minWidth": 90, "maxWidth": 200, "editable": True, "editCellData": {"type": "popUpButton", "items": table_masters}},
            {"title": "Par", "key": "pair", "width": 100, "minWidth": 80, "maxWidth": 150},
            {"title": "Ajuste", "key": "adjust", "width": 55, "minWidth": 45, "maxWidth": 70, "editable": True, "editCellData": {"type": "popUpButton", "items": self.kerning_adjust_options}},
            {"title": "Observação", "key": "note", "width": 325, "minWidth": 100, "maxWidth": 1000, "editable": True}
        ]
        kerningTab.kerningList = vanilla.List((0, 130, -0, -0), [],
                                             columnDescriptions=kerningColumns,
                                             doubleClickCallback=self.on_double_click_kerning,
                                             editCallback=self.on_edit_kerning_direct,
                                             allowsMultipleSelection=True,
                                             allowsSorting=True)
        kerningTab.kerningList.getNSTableView().setRowHeight_(22)

        self.kernLeftInput = kerningTab.leftInput
        self.kernRightInput = kerningTab.rightInput
        self.kernMasterSelect = kerningTab.masterSelect
        self.kernAdjustSelect = kerningTab.adjustSelect
        self.kernNoteInput = kerningTab.noteInput
        self.kerningList = kerningTab.kerningList
        self.kerningStatusFilterSelect = kerningTab.statusFilterSelect
        self.kerningAdjustFilterSelect = kerningTab.adjustFilterSelect
        self.kerningCounterText = kerningTab.counterText

        # ==================== ABA "TAREFAS" ====================
        tasksTab.taskInput = vanilla.EditText((0, 10, -82, 22), "", placeholder="Ex: criar tabular figures")
        tasksTab.removeTaskBtn = vanilla.Button((-74, 10, 32, 22), "➖", sizeStyle="small", callback=self.delete_selected_task_rows)
        tasksTab.addTaskBtn = vanilla.Button((-38, 10, -0, 22), "➕", callback=self.add_general_task)

        tasksTab.statusFilterLabel = vanilla.TextBox((0, 42, 50, 17), "Status:", sizeStyle="small")
        tasksTab.statusFilterSelect = vanilla.PopUpButton((52, 38, 120, 22), self.status_filters, callback=self.on_task_filter_changed)

        tasksTab.counterBox = vanilla.Box((0, 68, -0, 26))
        tasksTab.counterText = vanilla.TextBox((8, 72, -95, 18), "Resumo: 🔴 0  |  🟡 0  |  🟢 0  (Total: 0)", sizeStyle="small")
        tasksTab.filterRedBtn = vanilla.Button((-88, 70, 22, 18), "🔴", sizeStyle="small", callback=lambda s: self.set_task_status_filter(1))
        tasksTab.filterYellowBtn = vanilla.Button((-64, 70, 22, 18), "🟡", sizeStyle="small", callback=lambda s: self.set_task_status_filter(2))
        tasksTab.filterGreenBtn = vanilla.Button((-40, 70, 22, 18), "🟢", sizeStyle="small", callback=lambda s: self.set_task_status_filter(3))

        tasksTab.topLine = vanilla.HorizontalLine((0, 102, -0, 1))

        taskColumns = [
            {"title": "", "key": "status", "width": 28, "minWidth": 24, "maxWidth": 40},
            {"title": "Tarefa", "key": "task", "width": 480, "minWidth": 150, "maxWidth": 1000, "editable": True}
        ]
        tasksTab.taskList = vanilla.List((0, 110, -0, -0), [],
                                         columnDescriptions=taskColumns,
                                         doubleClickCallback=self.on_double_click_task,
                                         editCallback=self.save_data,
                                         allowsMultipleSelection=True,
                                         allowsSorting=True)
        tasksTab.taskList.getNSTableView().setRowHeight_(22)

        self.taskInput = tasksTab.taskInput
        self.taskList = tasksTab.taskList
        self.taskStatusFilterSelect = tasksTab.statusFilterSelect
        self.taskCounterText = tasksTab.counterText

        # --- RODAPÉ GLOBAL ---
        self.w.line2 = vanilla.HorizontalLine((12, -66, -12, 1))
        
        self.w.revLabel = vanilla.TextBox((12, -59, 110, 17), "Última revisão por:", sizeStyle="small")
        self.w.revInput = vanilla.EditText((125, -62, 180, 22), "", placeholder="Nome", sizeStyle="small", callback=self.save_reviewer)

        self.w.helpBtn = vanilla.Button((12, -30, 24, 22), "?", callback=self.show_help, sizeStyle="small")
        self.w.openPendingsBtn = vanilla.Button((42, -30, 125, 22), "Abrir selecionados", callback=self.open_pendings_in_tab, sizeStyle="small")
        self.w.copyMDBtn = vanilla.Button((173, -30, 115, 22), "Relatório (copiar)", callback=self.copy_markdown, sizeStyle="small")
        self.w.copyListBtn = vanilla.Button((294, -30, 100, 22), "Copiar Lista", callback=self.copy_glyph_list, sizeStyle="small")
        
        self.w.clearGlyphsBtn = vanilla.Button((-105, -30, -12, 22), "Limpar Glifos", callback=self.clear_all_glyphs, sizeStyle="small")
        self.w.clearKernBtn = vanilla.Button((-105, -30, -12, 22), "Limpar Kerning", callback=self.clear_all_kerning, sizeStyle="small")
        self.w.clearTasksBtn = vanilla.Button((-105, -30, -12, 22), "Limpar Tarefas", callback=self.clear_all_tasks, sizeStyle="small")
        
        self.w.clearKernBtn.show(False)
        self.w.clearTasksBtn.show(False)

        self.load_saved_data()
        self._updating_obs = False

        self.w.open()

    def on_tab_changed(self, sender):
        active_tab = sender.get()
        if active_tab == 0:
            self.w.openPendingsBtn.show(True)
            self.w.copyMDBtn.show(True)
            self.w.copyListBtn.show(True)
            self.w.clearGlyphsBtn.show(True)
            self.w.clearKernBtn.show(False)
            self.w.clearTasksBtn.show(False)
        elif active_tab == 1:
            self.w.openPendingsBtn.show(True)
            self.w.copyMDBtn.show(True)
            self.w.copyListBtn.show(False)
            self.w.clearGlyphsBtn.show(False)
            self.w.clearKernBtn.show(True)
            self.w.clearTasksBtn.show(False)
        else:
            self.w.openPendingsBtn.show(False)
            self.w.copyMDBtn.show(True)
            self.w.copyListBtn.show(False)
            self.w.clearGlyphsBtn.show(False)
            self.w.clearKernBtn.show(False)
            self.w.clearTasksBtn.show(True)

    # --- KERNING METHODS ---
    def add_kerning_action(self, sender):
        left = self.kernLeftInput.get().strip()
        right = self.kernRightInput.get().strip()

        if not left or not right:
            print("Digite ambos os glifos do par de kerning.")
            return

        font = Glyphs.font
        if not font:
            return

        selected_master = self.kernMasterSelect.getItem()
        adjust = self.kerning_adjust_options[self.kernAdjustSelect.get()]
        note = self.kernNoteInput.get().strip()

        display_pair = f"{left} {right}"

        all_kerns = [dict(k) for k in font.userData.get("reviewNotes_kerning_list", [])]
        all_kerns.append({
            "status": "🔴",
            "pair": display_pair,
            "left": left,
            "right": right,
            "master": selected_master,
            "adjust": adjust,
            "note": note
        })

        font.userData["reviewNotes_kerning_list"] = all_kerns
        self.kernLeftInput.set("")
        self.kernRightInput.set("")
        self.kernNoteInput.set("")
        self.refresh_kerning_table_view()

    def refresh_kerning_table_view(self):
        font = Glyphs.font
        if not font:
            return

        kerning_masters = [m for m in self.get_master_names() if m != "Todas"]
        self.kernMasterSelect.setItems(kerning_masters)
        if font.selectedFontMaster and font.selectedFontMaster.name in kerning_masters:
            self.kernMasterSelect.set(kerning_masters.index(font.selectedFontMaster.name))

        all_kerns = [dict(k) for k in font.userData.get("reviewNotes_kerning_list", [])]
        filtered = self.filter_kerning(all_kerns)
        self.kerningList.set(filtered)
        self.update_kerning_counters(all_kerns)

    def filter_kerning(self, all_kerns):
        filtered = list(all_kerns)
        status_idx = self.kerningStatusFilterSelect.get()
        if status_idx == 1:
            filtered = [k for k in filtered if k.get("status") == "🔴"]
        elif status_idx == 2:
            filtered = [k for k in filtered if k.get("status") == "🟡"]
        elif status_idx == 3:
            filtered = [k for k in filtered if k.get("status") == "🟢"]

        adjust_idx = self.kerningAdjustFilterSelect.get()
        if adjust_idx == 1:
            filtered = [k for k in filtered if k.get("adjust") == "+"]
        elif adjust_idx == 2:
            filtered = [k for k in filtered if k.get("adjust") == "-"]
        elif adjust_idx == 3:
            filtered = [k for k in filtered if k.get("adjust") == "?"]

        return filtered

    def update_kerning_counters(self, all_items):
        red_count = sum(1 for item in all_items if item.get("status") == "🔴")
        yellow_count = sum(1 for item in all_items if item.get("status") == "🟡")
        green_count = sum(1 for item in all_items if item.get("status") == "🟢")
        total = len(all_items)

        summary_str = f"Resumo: 🔴 {red_count}  |  🟡 {yellow_count}  |  🟢 {green_count}  (Total: {total})"
        self.kerningCounterText.set(summary_str)

    def on_edit_kerning_direct(self, sender):
        if self._updating_obs:
            return
        font = Glyphs.font
        if not font:
            return
        self._updating_obs = True
        try:
            current_visible = [dict(k) for k in sender.get()]
            all_kerns = [dict(k) for k in font.userData.get("reviewNotes_kerning_list", [])]
            
            for v_item in current_visible:
                for k_item in all_kerns:
                    if k_item.get("pair") == v_item.get("pair") and k_item.get("master") == v_item.get("master"):
                        k_item["adjust"] = v_item.get("adjust", k_item.get("adjust"))
                        k_item["note"] = v_item.get("note", k_item.get("note"))
                        k_item["master"] = v_item.get("master", k_item.get("master"))

            font.userData["reviewNotes_kerning_list"] = all_kerns
            self.update_kerning_counters(all_kerns)
        finally:
            self._updating_obs = False

    def on_kerning_filter_changed(self, sender):
        self.refresh_kerning_table_view()

    def set_kerning_status_filter(self, index):
        current = self.kerningStatusFilterSelect.get()
        if current == index:
            self.kerningStatusFilterSelect.set(0)
        else:
            self.kerningStatusFilterSelect.set(index)
        self.refresh_kerning_table_view()

    def delete_selected_kerning_rows(self, sender=None):
        selected = self.kerningList.getSelection()
        if not selected:
            print("Nenhum par de kerning selecionado para excluir.")
            return

        current_visible = [dict(k) for k in self.kerningList.get()]
        to_remove = {(current_visible[idx].get("pair"), current_visible[idx].get("master")) for idx in selected if idx < len(current_visible)}

        font = Glyphs.font
        if not font:
            return

        all_kerns = [dict(k) for k in font.userData.get("reviewNotes_kerning_list", [])]
        all_kerns = [k for k in all_kerns if (k.get("pair"), k.get("master")) not in to_remove]
        
        font.userData["reviewNotes_kerning_list"] = all_kerns
        self.refresh_kerning_table_view()

    def clear_all_kerning(self, sender):
        font = Glyphs.font
        if font:
            font.userData["reviewNotes_kerning_list"] = []
        self.refresh_kerning_table_view()

    def on_double_click_kerning(self, sender):
        table_view = sender.getNSTableView()
        selected_indexes = sender.getSelection()
        if not selected_indexes:
            return

        current_visible = [dict(k) for k in sender.get()]
        font = Glyphs.font
        if not font:
            return

        if table_view.clickedColumn() == 0:
            all_kerns = [dict(k) for k in font.userData.get("reviewNotes_kerning_list", [])]
            for idx in selected_indexes:
                if idx >= len(current_visible):
                    continue
                item = current_visible[idx]
                current_status = item.get("status", "🔴")
                new_status = self.status_cycles.get(current_status, "🔴")
                item["status"] = new_status

                for k_item in all_kerns:
                    if k_item.get("pair") == item.get("pair") and k_item.get("master") == item.get("master"):
                        k_item["status"] = new_status

            font.userData["reviewNotes_kerning_list"] = all_kerns
            self.refresh_kerning_table_view()

        else:
            item = current_visible[selected_indexes[0]]
            left_name, right_name = item.get("left"), item.get("right")

            glyph_l = font.glyphs[left_name]
            glyph_r = font.glyphs[right_name]

            if glyph_l and glyph_r:
                master_name = item.get("master")
                target_master = None
                for m in font.masters:
                    if m.name == master_name:
                        target_master = m
                        break
                if not target_master:
                    target_master = font.selectedFontMaster

                layer_l = glyph_l.layers[target_master.id]
                layer_r = glyph_r.layers[target_master.id]

                if layer_l and layer_r:
                    font.newTab([layer_l, layer_r])

    # --- BASE METHODS ---
    def get_available_groups(self):
        groups = ["Todos os Grupos", "Sem Grupo"]
        all_notes = self.read_notes_from_ud()
        existing = sorted(list(set(g.get("group", "").strip() for g in all_notes if g.get("group", "").strip())))
        groups.extend(existing)
        return groups

    def update_group_filter_menu(self):
        current_selection = self.groupFilterSelect.getItem()
        self.groups_list = self.get_available_groups()
        self.groupFilterSelect.setItems(self.groups_list)

        if current_selection in self.groups_list:
            self.groupFilterSelect.set(self.groups_list.index(current_selection))
        else:
            self.groupFilterSelect.set(0)

    def assign_group_to_selected(self, sender):
        new_group = self.assignGroupInput.get().strip()
        selection = self.list.getSelection()

        if not selection:
            print("Nenhum glifo selecionado para atribuir ao grupo.")
            return

        current_visible = self.list.get()
        if not current_visible:
            return

        selected_indexes = [int(i) for i in selection if int(i) < len(current_visible)]
        if not selected_indexes:
            return

        targets = set()
        for idx in selected_indexes:
            item = current_visible[idx]
            g_name = item.get("glyph")
            m_name = item.get("master", "Todas")
            if g_name:
                targets.add((g_name, m_name))

        all_notes = self.read_notes_from_ud()

        for note in all_notes:
            g_name = note.get("glyph")
            m_name = note.get("master", "Todas")
            if (g_name, m_name) in targets:
                note["group"] = new_group

        self.write_notes_to_ud(all_notes)
        self.assignGroupInput.set("")
        self.update_group_filter_menu()
        self.refresh_table_view()

    def manual_refresh_action(self, sender):
        self._color_image_cache.clear()
        self.refresh_table_view()

    def copy_to_clipboard(self, text):
        pb = NSPasteboard.generalPasteboard()
        pb.declareTypes_owner_([NSStringPboardType], None)
        pb.setString_forType_(text, NSStringPboardType)

    def copy_glyph_list(self, sender):
        current_list = self.list.get()
        if not current_list:
            print("Nenhum glifo na lista para copiar.")
            return

        glyph_names = []
        for item in current_list:
            g_name = item.get("glyph")
            if g_name and g_name not in glyph_names:
                glyph_names.append(g_name)

        if glyph_names:
            text_to_copy = "\n".join(glyph_names)
            self.copy_to_clipboard(text_to_copy)
            print(f"{len(glyph_names)} glifo(s) copiado(s) para a área de transferência!")

    def get_secondary_color(self):
        return NSColor.secondaryLabelColor()

    def get_current_file_name(self):
        font = Glyphs.font
        if not font or not font.filepath:
            return "Sem arquivo salvo"
        return font.filepath.split("/")[-1]

    def get_color_image(self, glyph_color, layer_color):
        cache_key = (str(glyph_color), str(layer_color))
        if cache_key in self._color_image_cache:
            return self._color_image_cache[cache_key]

        size = NSSize(14, 14)
        image = NSImage.alloc().initWithSize_(size)
        image.lockFocus()

        palette = [
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.94, 0.33, 0.31, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.98, 0.60, 0.20, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.71, 0.49, 0.30, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.98, 0.85, 0.27, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.61, 0.83, 0.35, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.20, 0.70, 0.30, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.40, 0.78, 0.95, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.20, 0.50, 0.85, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.60, 0.40, 0.80, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.90, 0.40, 0.70, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.75, 0.75, 0.75, 1.0),
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.35, 0.35, 0.35, 1.0),
        ]

        def get_nscolor(val):
            if val is None or val == -1:
                return None
            if hasattr(val, "CGColor"):
                return val
            if isinstance(val, int) and 0 <= val < len(palette):
                return palette[val]
            return None

        g_col = get_nscolor(glyph_color)
        l_col = get_nscolor(layer_color)

        rect = NSRect((1, 1), (12, 12))
        path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(rect, 2.0, 2.0)

        if g_col is None and l_col is None:
            NSColor.separatorColor().set()
            path.setLineWidth_(1.0)
            path.stroke()
        elif l_col is None:
            g_col.set()
            path.fill()
        elif g_col is None:
            l_col.set()
            path.fill()
        else:
            path.addClip()
            g_col.set()
            NSBezierPath.fillRect_(rect)

            tri = NSBezierPath.alloc().init()
            tri.moveToPoint_((1, 1))
            tri.lineToPoint_((13, 1))
            tri.lineToPoint_((13, 13))
            tri.closePath()
            l_col.set()
            tri.fill()

        image.unlockFocus()
        self._color_image_cache[cache_key] = image
        return image

    def get_item_color_info(self, item):
        font = Glyphs.font
        if not font:
            return self.get_color_image(-1, -1), -1
        glyph_name = item.get("glyph")
        master_name = item.get("master")
        glyph = font.glyphs[glyph_name]
        if not glyph:
            return self.get_color_image(-1, -1), -1

        g_color = glyph.color if hasattr(glyph, "color") and glyph.color is not None else -1

        target_master = None
        if master_name and master_name != "Todas":
            for m in font.masters:
                if m.name == master_name:
                    target_master = m
                    break
        if not target_master and font.masters:
            target_master = font.selectedFontMaster

        l_color = -1
        if target_master:
            layer = glyph.layers[target_master.id]
            if layer and hasattr(layer, "color") and layer.color is not None:
                l_color = layer.color

        img = self.get_color_image(g_color, l_color)
        sort_index = (g_color if g_color != -1 else 999) * 100 + (l_color if l_color != -1 else 999)
        return img, sort_index

    def show_help(self, sender):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Como utilizar o Controle de Projeto")
        alert.setInformativeText_(
            "• Aba Glifos:\n"
            "  - Adicione por digitação ou seleção ativa na Edit View. Marque 'Todas masters' para replicar.\n"
            "  - Organize atribuindo grupos com '📁+' e filtre por Master, Grupo, Status, Eixo ou Busca Livre.\n\n"
            "• Aba Kerning:\n"
            "  - Adicione pares na seção 'Insira Pares de Glifos' indicando a Master, os glifos Esq/Dir, a ação (+ Aumentar, - Diminuir, ? Verificar) e uma Observação.\n"
            "  - Dê duplo clique em uma linha para abrir o par diretamente em uma nova aba de edição.\n\n"
            "• Aba Tarefas:\n"
            "  - Gerencie pendências gerais de projeto desvinculadas de glifos específicos.\n\n"
            "• Recursos Gerais:\n"
            "  - Clique duplo na primeira coluna (ícone de status) para alternar entre 🔴 Pendente, 🟡 Em Processo e 🟢 Concluído.\n"
            "  - O painel 'Resumo' mantém a contagem global fixa de cada aba.\n"
            "  - 'Abrir selecionados' abre os itens marcados na tabela diretamente para edição.\n"
            "  - Use 'Relatório (copiar)' para exportar um resumo estruturado em Markdown."
        )
        alert.addButtonWithTitle_("Entendido")
        alert.runModal()

    def set_status_filter(self, index):
        current = self.statusFilterSelect.get()
        if current == index:
            self.statusFilterSelect.set(0)
        else:
            self.statusFilterSelect.set(index)
        self.refresh_table_view()

    def set_task_status_filter(self, index):
        current = self.taskStatusFilterSelect.get()
        if current == index:
            self.taskStatusFilterSelect.set(0)
        else:
            self.taskStatusFilterSelect.set(index)
        self.refresh_task_table_view()

    def get_master_names(self):
        masters = ["Todas"]
        font = Glyphs.font
        if font and font.masters:
            masters.extend([m.name for m in font.masters])
        return masters

    def get_available_axes_filters(self):
        axes_options = ["Todos os Eixos"]
        font = Glyphs.font
        if not font or not font.axes or not font.masters:
            return axes_options

        for axis_idx, axis in enumerate(font.axes):
            axis_name = axis.name or f"Eixo {axis_idx + 1}"
            axis_tag = axis.tag if hasattr(axis, "tag") else axis_name

            values = sorted(list(set(master.axes[axis_idx] for master in font.masters if len(master.axes) > axis_idx)))
            for val in values:
                val_str = int(val) if float(val).is_integer() else val
                axes_options.append(f"{axis_tag}: {val_str}")

        return axes_options

    def get_active_master_filter(self):
        idx = self.topMasterSelect.get()
        if idx < len(self.masters_list):
            return self.masters_list[idx]
        return "Todas"

    def update_counters(self, all_items):
        red_count = sum(1 for item in all_items if item.get("status") == "🔴")
        yellow_count = sum(1 for item in all_items if item.get("status") == "🟡")
        green_count = sum(1 for item in all_items if item.get("status") == "🟢")
        total = len(all_items)

        summary_str = f"Resumo: 🔴 {red_count}  |  🟡 {yellow_count}  |  🟢 {green_count}  (Total: {total})"
        self.counterText.set(summary_str)

    def update_task_counters(self, all_items):
        red_count = sum(1 for item in all_items if item.get("status") == "🔴")
        yellow_count = sum(1 for item in all_items if item.get("status") == "🟡")
        green_count = sum(1 for item in all_items if item.get("status") == "🟢")
        total = len(all_items)

        summary_str = f"Resumo: 🔴 {red_count}  |  🟡 {yellow_count}  |  🟢 {green_count}  (Total: {total})"
        self.taskCounterText.set(summary_str)

    def read_notes_from_ud(self):
        font = Glyphs.font
        if not font:
            return []
        items = []
        for item in font.userData.get("reviewNotes_list", []):
            d = dict(item)
            img, sort_idx = self.get_item_color_info(d)
            d["colorIcon"] = img
            d["_colorSort"] = sort_idx
            if "group" not in d:
                d["group"] = ""
            items.append(d)
        return items

    def write_notes_to_ud(self, notes):
        font = Glyphs.font
        if not font:
            return
        clean_notes = []
        for n in notes:
            copy_n = dict(n)
            if "colorIcon" in copy_n:
                del copy_n["colorIcon"]
            if "_colorSort" in copy_n:
                del copy_n["_colorSort"]
            clean_notes.append(copy_n)
        font.userData["reviewNotes_list"] = clean_notes

    def save_reviewer(self, sender):
        font = Glyphs.font
        if not font:
            return
        reviewer_name = sender.get().strip()
        font.userData["reviewNotes_reviewer"] = reviewer_name

    def load_saved_data(self):
        font = Glyphs.font
        if not font:
            return

        saved_reviewer = font.userData.get("reviewNotes_reviewer", "")
        self.w.revInput.set(saved_reviewer)

        self.refresh_task_table_view()
        self.refresh_kerning_table_view()
        self.update_group_filter_menu()
        self.refresh_table_view()

    def filter_notes(self, all_notes):
        font = Glyphs.font
        filtered = list(all_notes)

        # Filtro por Master
        selected_master = self.get_active_master_filter()
        if selected_master != "Todas":
            filtered = [item for item in filtered if item.get("master") == selected_master]

        # Filtro por Grupo
        group_idx = self.groupFilterSelect.get()
        if group_idx > 0 and group_idx < len(self.groups_list):
            selected_group = self.groups_list[group_idx]
            if selected_group == "Sem Grupo":
                filtered = [item for item in filtered if not item.get("group", "").strip()]
            else:
                filtered = [item for item in filtered if item.get("group") == selected_group]

        # Filtro por Status
        status_idx = self.statusFilterSelect.get()
        if status_idx == 1:
            filtered = [item for item in filtered if item.get("status") == "🔴"]
        elif status_idx == 2:
            filtered = [item for item in filtered if item.get("status") == "🟡"]
        elif status_idx == 3:
            filtered = [item for item in filtered if item.get("status") == "🟢"]

        # Busca Geral
        search_query = self.searchInput.get().strip().lower()
        if search_query:
            filtered = [
                item for item in filtered
                if search_query in item.get("glyph", "").lower() 
                or search_query in item.get("obs", "").lower()
                or search_query in item.get("group", "").lower()
            ]

        # Filtro por Eixo
        axis_idx = self.axisFilterSelect.get()
        if font and axis_idx > 0 and axis_idx < len(self.axes_filters):
            selected_axis_str = self.axes_filters[axis_idx]
            if ":" in selected_axis_str:
                tag, val = selected_axis_str.split(":")
                tag = tag.strip()
                val = float(val.strip())

                valid_masters = []
                for m in font.masters:
                    for a_idx, a in enumerate(font.axes):
                        a_tag = a.tag if hasattr(a, "tag") else a.name
                        if a_tag == tag and len(m.axes) > a_idx and m.axes[a_idx] == val:
                            valid_masters.append(m.name)

                filtered = [item for item in filtered if item.get("master") in valid_masters]

        return filtered

    def filter_tasks(self, all_tasks):
        filtered = list(all_tasks)
        status_idx = self.taskStatusFilterSelect.get()
        if status_idx == 1:
            filtered = [t for t in filtered if t.get("status") == "🔴"]
        elif status_idx == 2:
            filtered = [t for t in filtered if t.get("status") == "🟡"]
        elif status_idx == 3:
            filtered = [t for t in filtered if t.get("status") == "🟢"]
        return filtered

    def refresh_table_view(self):
        all_notes = self.read_notes_from_ud()
        if not all_notes and not Glyphs.font:
            return

        filtered = self.filter_notes(all_notes)
        self.list.set(filtered)
        self.update_counters(all_notes)

    def refresh_task_table_view(self):
        font = Glyphs.font
        if not font:
            return
        all_tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])]
        filtered = self.filter_tasks(all_tasks)
        self.taskList.set(filtered)
        self.update_task_counters(all_tasks)

    def save_data(self, sender=None):
        if self._updating_obs:
            return
        font = Glyphs.font
        if not font:
            return
        self._updating_obs = True
        try:
            current_visible = [dict(t) for t in self.taskList.get()]
            all_tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])]
            
            for v_item in current_visible:
                for t_item in all_tasks:
                    if t_item.get("task") == v_item.get("task"):
                        t_item["task"] = v_item.get("task")

            font.userData["reviewNotes_general_tasks"] = all_tasks
            self.update_task_counters(all_tasks)
        finally:
            self._updating_obs = False

    def on_filter_changed(self, sender):
        self.refresh_table_view()

    def on_task_filter_changed(self, sender):
        self.refresh_task_table_view()

    def add_glyphs_action(self, sender):
        font = Glyphs.font
        if not font:
            print("Nenhuma fonte aberta.")
            return

        self.masters_list = self.get_master_names()
        self.topMasterSelect.setItems(self.masters_list)

        add_to_all_masters = self.allMastersCheck.get()
        manual_text = self.manualGlyphInput.get().strip()

        if add_to_all_masters:
            target_masters = [m.name for m in font.masters] if font.masters else ["Todas"]
            self.topMasterSelect.set(0)
        else:
            current_active_master = font.selectedFontMaster.name if font.selectedFontMaster else "Todas"
            target_masters = [current_active_master]
            if current_active_master in self.masters_list:
                self.topMasterSelect.set(self.masters_list.index(current_active_master))

        glyph_names_to_add = []

        if manual_text:
            cleaned_text = manual_text.replace(",", " ").replace("/", " ")
            glyph_names_to_add = [g.strip() for g in cleaned_text.split() if g.strip()]
        elif font.selectedLayers:
            for layer in font.selectedLayers:
                if layer.parent:
                    glyph_names_to_add.append(layer.parent.name)

        if not glyph_names_to_add:
            print("Nenhum glifo digitado ou selecionado.")
            return

        all_notes = self.read_notes_from_ud()

        for glyph_name in glyph_names_to_add:
            for master_name in target_masters:
                if not any(item["glyph"] == glyph_name and item["master"] == master_name for item in all_notes):
                    all_notes.append({
                        "status": "🔴",
                        "group": "",
                        "master": master_name,
                        "glyph": glyph_name,
                        "obs": ""
                    })

        self.write_notes_to_ud(all_notes)
        self.manualGlyphInput.set("")
        self.update_group_filter_menu()
        self.refresh_table_view()

    def on_edit_obs_direct(self, sender):
        if self._updating_obs:
            return

        font = Glyphs.font
        if not font:
            return

        self._updating_obs = True
        try:
            current_visible_items = [dict(i) for i in sender.get()]
            all_notes = self.read_notes_from_ud()

            for visible_item in current_visible_items:
                v_glyph = visible_item.get("glyph")
                v_master = visible_item.get("master", "Todas")
                v_group = visible_item.get("group", "")
                v_obs = visible_item.get("obs", "")
                v_status = visible_item.get("status", "🔴")

                for global_item in all_notes:
                    if global_item.get("glyph") == v_glyph and global_item.get("master") == v_master:
                        global_item["group"] = v_group
                        global_item["master"] = v_master
                        global_item["obs"] = v_obs
                        global_item["status"] = v_status

            self.write_notes_to_ud(all_notes)
            self.update_group_filter_menu()
            self.update_counters(all_notes)
        finally:
            self._updating_obs = False

    def clear_all_glyphs(self, sender):
        font = Glyphs.font
        if font:
            font.userData["reviewNotes_list"] = []
        self.update_group_filter_menu()
        self.refresh_table_view()

    def clear_all_tasks(self, sender):
        font = Glyphs.font
        if font:
            font.userData["reviewNotes_general_tasks"] = []
        self.refresh_task_table_view()

    def add_general_task(self, sender):
        task_text = self.taskInput.get().strip()
        if not task_text:
            return

        font = Glyphs.font
        if not font:
            return

        tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])]
        tasks.append({
            "status": "🔴",
            "task": task_text
        })
        font.userData["reviewNotes_general_tasks"] = tasks
        self.taskInput.set("")
        self.refresh_task_table_view()

    def on_double_click_task(self, sender):
        table_view = sender.getNSTableView()
        if table_view.clickedColumn() != 0:
            return

        selected_indexes = sender.getSelection()
        if not selected_indexes:
            return

        current_visible = [dict(t) for t in sender.get()]
        font = Glyphs.font
        if not font:
            return
        all_tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])]

        for idx in selected_indexes:
            if idx >= len(current_visible):
                continue
            item = current_visible[idx]
            current_status = item.get("status", "🔴")
            new_status = self.status_cycles.get(current_status, "🔴")
            item["status"] = new_status

            for g_item in all_tasks:
                if g_item.get("task") == item.get("task"):
                    g_item["status"] = new_status

        font.userData["reviewNotes_general_tasks"] = all_tasks
        self.refresh_task_table_view()

    def on_double_click_row(self, sender):
        table_view = sender.getNSTableView()
        if table_view.clickedColumn() != 0:
            return

        selected_indexes = sender.getSelection()
        if not selected_indexes:
            return

        current_list = [dict(i) for i in sender.get()]
        all_notes = self.read_notes_from_ud()

        for idx in selected_indexes:
            if idx >= len(current_list):
                continue
            item = current_list[idx]
            current_status = item.get("status", "🔴")
            new_status = self.status_cycles.get(current_status, "🔴")
            item["status"] = new_status

            for global_item in all_notes:
                if global_item.get("master") == item.get("master") and global_item.get("glyph") == item.get("glyph"):
                    global_item["status"] = new_status

        self.write_notes_to_ud(all_notes)
        self.refresh_table_view()

    def delete_selected_glyph_rows(self, sender=None):
        selected = self.list.getSelection()
        if not selected:
            print("Nenhuma linha selecionada para excluir.")
            return

        current = self.list.get()
        to_remove = set()
        for idx in selected:
            if idx < len(current):
                item = current[idx]
                to_remove.add((item.get("master"), item.get("glyph")))

        if not to_remove:
            return

        all_notes = self.read_notes_from_ud()
        all_notes = [
            g for g in all_notes
            if (g.get("master"), g.get("glyph")) not in to_remove
        ]
        self.write_notes_to_ud(all_notes)
        self.update_group_filter_menu()
        self.refresh_table_view()

    def delete_selected_task_rows(self, sender=None):
        selected = self.taskList.getSelection()
        if not selected:
            print("Nenhuma tarefa selecionada para excluir.")
            return

        current_visible = [dict(t) for t in self.taskList.get()]
        to_remove_tasks = {current_visible[idx].get("task") for idx in selected if idx < len(current_visible)}

        font = Glyphs.font
        if not font:
            return

        all_tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])]
        all_tasks = [t for t in all_tasks if t.get("task") not in to_remove_tasks]
        
        font.userData["reviewNotes_general_tasks"] = all_tasks
        self.refresh_task_table_view()

    def open_pendings_in_tab(self, sender):
        font = Glyphs.font
        if not font:
            return

        active_tab = self.w.tabs.get()

        # Aba de Glifos
        if active_tab == 0:
            selected_indexes = self.list.getSelection()
            if not selected_indexes:
                print("Nenhum glifo selecionado na tabela para abrir.")
                return

            current_list = self.list.get()
            selected_items = [current_list[i] for i in selected_indexes if i < len(current_list)]

            layers_to_open = []
            for item in selected_items:
                glyph_name = item.get("glyph")
                master_name = item.get("master")

                glyph = font.glyphs[glyph_name]
                if not glyph:
                    continue

                target_master = None
                if master_name and master_name != "Todas":
                    for m in font.masters:
                        if m.name == master_name:
                            target_master = m
                            break

                if not target_master:
                    target_master = font.selectedFontMaster

                layer = glyph.layers[target_master.id]
                if layer:
                    layers_to_open.append(layer)

            if layers_to_open:
                font.newTab(layers_to_open)

        # Aba de Kerning
        elif active_tab == 1:
            selected_indexes = self.kerningList.getSelection()
            if not selected_indexes:
                print("Nenhum par de kerning selecionado para abrir.")
                return

            current_list = self.kerningList.get()
            selected_items = [current_list[i] for i in selected_indexes if i < len(current_list)]

            layers_to_open = []
            for item in selected_items:
                left_name, right_name = item.get("left"), item.get("right")
                glyph_l, glyph_r = font.glyphs[left_name], font.glyphs[right_name]

                if glyph_l and glyph_r:
                    master_name = item.get("master")
                    target_master = None
                    for m in font.masters:
                        if m.name == master_name:
                            target_master = m
                            break
                    if not target_master:
                        target_master = font.selectedFontMaster

                    layer_l = glyph_l.layers[target_master.id]
                    layer_r = glyph_r.layers[target_master.id]

                    if layer_l and layer_r:
                        layers_to_open.extend([layer_l, layer_r])

            if layers_to_open:
                font.newTab(layers_to_open)

    def copy_markdown(self, sender):
        font = Glyphs.font
        family_name = font.familyName if font and font.familyName else "Desconhecida"
        file_path = font.filepath if font and font.filepath else "Não salvo"
        file_name = file_path.split("/")[-1] if file_path != "Não salvo" else "Não salvo"
        now_str = datetime.datetime.now().strftime("%d/%m/%Y | %H:%M")

        reviewer = font.userData.get("reviewNotes_reviewer", "") if font else ""
        active_tab = self.w.tabs.get()

        md_text = f"# Relatório de Projeto ({family_name})\n\n"
        md_text += f"Arquivo: {file_name}\n"
        md_text += f"Data: {now_str}\n"
        if reviewer:
            md_text += f"Revisado por: {reviewer}\n"
        md_text += "\n"

        # Exportação de Glifos + Tarefas (Aba Glifos)
        if active_tab == 0:
            selected_master = self.get_active_master_filter()
            items = self.read_notes_from_ud()
            if selected_master != "Todas":
                items = [item for item in items if item.get("master") == selected_master]

            tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])] if font else []

            if not items and not tasks:
                print("Nenhum dado de Glifos ou Tarefas para copiar.")
                return

            if tasks:
                md_text += "## Tarefas Gerais do Projeto:\n"
                for t in tasks:
                    status_icon = t.get('status', '🔴')
                    md_text += f"[{status_icon}] {t.get('task', '')}\n"
                md_text += "\n"

            if items:
                md_text += f"## Glifos (Visualização: {selected_master}):\n"
                max_group_len = max([len(item.get("group", "")) for item in items] + [len("Grupo")]) + 4
                max_master_len = max([len(item.get("master", "")) for item in items] + [len("Master")]) + 4
                max_glyph_len = max([len(item.get("glyph", "")) for item in items] + [len("Glifo")]) + 4

                header = f"{'Status':<10} {'Grupo':<{max_group_len}} {'Master':<{max_master_len}} {'Glifo':<{max_glyph_len}} Obs."
                separator = "-" * (len(header) + 20)

                md_text += header + "\n"
                md_text += separator + "\n"

                for item in items:
                    status_str = f"[{item.get('status', '🔴')}]"
                    group_str = item.get("group", "")
                    master_str = item.get("master", "")
                    glyph_str = item.get("glyph", "")
                    obs_str = item.get("obs", "")

                    md_text += f"{status_str:<10} {group_str:<{max_group_len}} {master_str:<{max_master_len}} {glyph_str:<{max_glyph_len}} {obs_str}\n"

        # Exportação Exclusiva de Kerning (Aba Kerning)
        elif active_tab == 1:
            kerns = [dict(k) for k in font.userData.get("reviewNotes_kerning_list", [])] if font else []

            if not kerns:
                print("Nenhum registro de Kerning para copiar.")
                return

            md_text += "## Ajustes de Kerning:\n\n"
            max_master_len = max([len(k.get("master", "")) for k in kerns] + [len("Master")]) + 4
            max_pair_len = max([len(k.get("pair", "")) for k in kerns] + [len("Par")]) + 4
            max_adjust_len = max([len(k.get("adjust", "")) for k in kerns] + [len("Ajuste")]) + 4

            header = f"{'Status':<10} {'Master':<{max_master_len}} {'Par':<{max_pair_len}} {'Ajuste':<{max_adjust_len}} Observação"
            separator = "-" * (len(header) + 20)

            md_text += header + "\n"
            md_text += separator + "\n"

            for k in kerns:
                status_str = f"[{k.get('status', '🔴')}]"
                master_str = k.get("master", "")
                pair_str = k.get("pair", "")
                adjust_str = k.get("adjust", "")
                note_str = k.get("note", "")

                md_text += f"{status_str:<10} {master_str:<{max_master_len}} {pair_str:<{max_pair_len}} {adjust_str:<{max_adjust_len}} {note_str}\n"

        # Exportação Exclusiva de Tarefas (Aba Tarefas)
        else:
            tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])] if font else []

            if not tasks:
                print("Nenhuma tarefa para copiar.")
                return

            md_text += "## Tarefas Gerais do Projeto:\n\n"
            for t in tasks:
                status_icon = t.get('status', '🔴')
                md_text += f"[{status_icon}] {t.get('task', '')}\n"

        self.copy_to_clipboard(md_text)
        print("Relatório copiado com sucesso!")

ReviewNotesFloatingWindow()
