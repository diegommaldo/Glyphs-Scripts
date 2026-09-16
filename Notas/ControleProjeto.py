# MenuTitle: Controle de Projeto
# -*- coding: utf-8 -*-
__doc__ = """
Abre janela avançada de notas para 
desenvolvimento de projeto.
"""

import datetime
import vanilla
from AppKit import NSPasteboard, NSStringPboardType, NSAlert, NSImage, NSSize, NSBezierPath, NSColor, NSRect, NSImageCell, NSNotificationCenter
from GlyphsApp import UPDATEINTERFACE

class ReviewNotesFloatingWindow(object):
    def __init__(self):
        Glyphs.clearLog()

        self._updating_obs = True

        self.status_cycles = {
            "🔴": "🟡",
            "🟡": "🟢",
            "🟢": "🔴"
        }

        self.masters_list = self.get_master_names()
        self.status_filters = ["Todos Status", "🔴 Pendentes", "🟡 Em Processo", "🟢 Concluídos"]
        self.axes_filters = self.get_available_axes_filters()

        self.w = vanilla.FloatingWindow((610, 660), "Controle de Projeto", minSize=(500, 470))

        file_name = self.get_current_file_name()
        self.w.fileHeaderLabel = vanilla.TextBox((12, 12, -12, 18), f"Arquivo: {file_name}", sizeStyle="small")
        self.w.fileHeaderLabel.getNSTextField().setTextColor_(self.get_secondary_color())

        self.w.tabs = vanilla.Tabs((12, 34, -12, -72), ["Glifos", "Tarefas"], callback=self.on_tab_changed)
        glyphsTab = self.w.tabs[0]
        tasksTab = self.w.tabs[1]

        # ==================== ABA "GLIFOS" ====================
        glyphsTab.topMasterLabel = vanilla.TextBox((0, 10, 50, 17), "Master:", sizeStyle="small")
        glyphsTab.topMasterSelect = vanilla.PopUpButton((52, 6, 110, 22), self.masters_list, callback=self.on_filter_changed)
        glyphsTab.manualGlyphInput = vanilla.EditText((170, 6, 190, 22), "", placeholder="ex: a, b, c")
        glyphsTab.addBtn = vanilla.Button((366, 6, 32, 22), "➕", callback=self.add_glyphs_action)
        glyphsTab.allMastersCheck = vanilla.CheckBox((408, 8, 115, 18), "Todas masters", sizeStyle="small", value=False)

        glyphsTab.statusFilterLabel = vanilla.TextBox((0, 42, 50, 17), "Status:", sizeStyle="small")
        glyphsTab.statusFilterSelect = vanilla.PopUpButton((52, 38, 120, 22), self.status_filters, callback=self.on_filter_changed)
        glyphsTab.searchInput = vanilla.EditText((178, 38, -0, 22), "", placeholder="🔍 Buscar glifo ou obs...", callback=self.on_filter_changed)

        glyphsTab.axisFilterLabel = vanilla.TextBox((0, 74, 50, 17), "Eixo:", sizeStyle="small")
        glyphsTab.axisFilterSelect = vanilla.PopUpButton((52, 70, -0, 22), self.axes_filters, callback=self.on_filter_changed)

        glyphsTab.counterBox = vanilla.Box((0, 102, -0, 26))
        glyphsTab.counterText = vanilla.TextBox((8, 106, -118, 18), "Resumo: 🔴 0  |  🟡 0  |  🟢 0  (Total: 0)", sizeStyle="small")
        glyphsTab.filterRedBtn = vanilla.Button((-112, 104, 22, 18), "🔴", sizeStyle="small", callback=lambda s: self.set_status_filter(1))
        glyphsTab.filterYellowBtn = vanilla.Button((-88, 104, 22, 18), "🟡", sizeStyle="small", callback=lambda s: self.set_status_filter(2))
        glyphsTab.filterGreenBtn = vanilla.Button((-64, 104, 22, 18), "🟢", sizeStyle="small", callback=lambda s: self.set_status_filter(3))
        glyphsTab.removeGlyphBtn = vanilla.Button((-38, 103, 30, 20), "➖", sizeStyle="small", callback=self.delete_selected_glyph_rows)

        glyphsTab.topLine = vanilla.HorizontalLine((0, 138, -0, 1))

        table_masters = [m for m in self.masters_list if m != "Todas"]
        columnDescriptions = [
            {"title": "", "key": "status", "width": 28, "minWidth": 24, "maxWidth": 40},
            {"title": "Master", "key": "master", "width": 110, "minWidth": 110, "maxWidth": 250, "editable": True, "editCellData": {"type": "popUpButton", "items": table_masters}},
            {"title": "Glifo", "key": "glyph", "width": 85, "minWidth": 70, "maxWidth": 200},
            {"title": "Cor", "key": "colorIcon", "width": 32, "minWidth": 32, "maxWidth": 40},
            {"title": "Observações", "key": "obs", "width": 250, "minWidth": 100, "maxWidth": 1000, "editable": True}
        ]
        glyphsTab.list = vanilla.List((0, 146, -0, -0), [],
                                     columnDescriptions=columnDescriptions,
                                     doubleClickCallback=self.on_double_click_row,
                                     editCallback=self.on_edit_obs_direct,
                                     allowsMultipleSelection=True)
        
        table_view = glyphsTab.list.getNSTableView()
        table_view.setRowHeight_(22)
        color_column = table_view.tableColumnWithIdentifier_("colorIcon")
        if color_column:
            image_cell = NSImageCell.alloc().init()
            color_column.setDataCell_(image_cell)

        self.topMasterSelect = glyphsTab.topMasterSelect
        self.allMastersCheck = glyphsTab.allMastersCheck
        self.manualGlyphInput = glyphsTab.manualGlyphInput
        self.statusFilterSelect = glyphsTab.statusFilterSelect
        self.searchInput = glyphsTab.searchInput
        self.axisFilterSelect = glyphsTab.axisFilterSelect
        self.counterText = glyphsTab.counterText
        self.list = glyphsTab.list

        # ==================== ABA "TAREFAS" ====================
        tasksTab.taskInput = vanilla.EditText((0, 10, -82, 22), "", placeholder="ex: criar tabular figures")
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
                                         allowsMultipleSelection=True)
        tasksTab.taskList.getNSTableView().setRowHeight_(22)

        self.taskInput = tasksTab.taskInput
        self.taskList = tasksTab.taskList
        self.taskStatusFilterSelect = tasksTab.statusFilterSelect
        self.taskCounterText = tasksTab.counterText

        # --- RODAPÉ GLOBAL ---
        self.w.line2 = vanilla.HorizontalLine((12, -66, -12, 1))
        
        self.w.revLabel = vanilla.TextBox((12, -59, 110, 17), "Última revisão por:", sizeStyle="small")
        self.w.revInput = vanilla.EditText((125, -62, 200, 22), "", placeholder="Nome", sizeStyle="small", callback=self.save_reviewer)

        self.w.helpBtn = vanilla.Button((12, -30, 24, 22), "?", callback=self.show_help, sizeStyle="small")
        self.w.openPendingsBtn = vanilla.Button((42, -30, 135, 22), "Abrir selecionados", callback=self.open_pendings_in_tab, sizeStyle="small")
        self.w.copyMDBtn = vanilla.Button((183, -30, 115, 22), "Relatório (copiar)", callback=self.copy_markdown, sizeStyle="small")
        
        self.w.clearGlyphsBtn = vanilla.Button((-105, -30, -12, 22), "Limpar Glifos", callback=self.clear_all_glyphs, sizeStyle="small")
        self.w.clearTasksBtn = vanilla.Button((-105, -30, -12, 22), "Limpar Tarefas", callback=self.clear_all_tasks, sizeStyle="small")
        self.w.clearTasksBtn.show(False)

        # Registra observadores de notificação do macOS
        nc = NSNotificationCenter.defaultCenter()
        nc.addObserver_selector_name_object_(self, "update_colors_event:", "GSUpdateInterface", None)
        nc.addObserver_selector_name_object_(self, "update_colors_event:", "GSDocumentDidChangeNotification", None)
        nc.addObserver_selector_name_object_(self, "update_colors_event:", "GSCallbackHandledNotification", None)

        # Callback nativo do Glyphs
        Glyphs.addCallback(self.update_colors_event_, UPDATEINTERFACE)

        self.w.bind("close", self.window_will_close)

        self.load_saved_data()
        self._updating_obs = False

        self.w.open()

    def update_colors_event_(self, sender=None):
        if not self._updating_obs:
            self.refresh_table_view()

    def window_will_close(self, sender):
        nc = NSNotificationCenter.defaultCenter()
        nc.removeObserver_name_object_(self, "GSUpdateInterface", None)
        nc.removeObserver_name_object_(self, "GSDocumentDidChangeNotification", None)
        nc.removeObserver_name_object_(self, "GSCallbackHandledNotification", None)
        try:
            Glyphs.removeCallback(self.update_colors_event_, UPDATEINTERFACE)
        except:
            pass

    def get_secondary_color(self):
        return NSColor.secondaryLabelColor()

    def get_current_file_name(self):
        font = Glyphs.font
        if not font or not font.filepath:
            return "Sem arquivo salvo"
        return font.filepath.split("/")[-1]

    def get_color_image(self, glyph_color, layer_color):
        size = NSSize(14, 14)
        image = NSImage.alloc().initWithSize_(size)
        image.lockFocus()

        palette = [
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.94, 0.33, 0.31, 1.0), # 0: Red
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.98, 0.60, 0.20, 1.0), # 1: Orange
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.71, 0.49, 0.30, 1.0), # 2: Brown
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.98, 0.85, 0.27, 1.0), # 3: Yellow
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.61, 0.83, 0.35, 1.0), # 4: Light Green
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.20, 0.70, 0.30, 1.0), # 5: Green
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.40, 0.78, 0.95, 1.0), # 6: Light Blue
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.20, 0.50, 0.85, 1.0), # 7: Blue
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.60, 0.40, 0.80, 1.0), # 8: Purple
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.90, 0.40, 0.70, 1.0), # 9: Magenta
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.75, 0.75, 0.75, 1.0), # 10: Light Gray
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.35, 0.35, 0.35, 1.0), # 11: Dark Gray
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
        return image

    def get_item_color_icon(self, item):
        font = Glyphs.font
        if not font:
            return self.get_color_image(-1, -1)
        glyph_name = item.get("glyph")
        master_name = item.get("master")
        glyph = font.glyphs[glyph_name]
        if not glyph:
            return self.get_color_image(-1, -1)

        g_color = glyph.color if hasattr(glyph, "color") else -1

        target_master = None
        if master_name and master_name != "Geral":
            for m in font.masters:
                if m.name == master_name:
                    target_master = m
                    break
        if not target_master and font.masters:
            target_master = font.selectedFontMaster

        l_color = -1
        if target_master:
            layer = glyph.layers[target_master.id]
            if layer and hasattr(layer, "color"):
                l_color = layer.color

        return self.get_color_image(g_color, l_color)

    def show_help(self, sender):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Como utilizar o Controle de Projeto")
        alert.setInformativeText_(
            "• Adicione glifos digitando os nomes ou selecionando-os na Edit View.\n\n"
            "• Use o campo de busca para filtrar por nome ou observação.\n\n"
            "• Clique nos botões de status (🔴, 🟡, 🟢) no resumo para filtro rápido.\n\n"
            "• Dê duplo clique no círculo de status da tabela para alterar o progresso.\n\n"
            "• Clique na coluna 'Master' ou 'Observações' para editá-las diretamente."
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

    def on_tab_changed(self, sender):
        active_tab = sender.get()
        if active_tab == 0:
            self.w.openPendingsBtn.show(True)
            self.w.copyMDBtn.show(True)
            self.w.clearGlyphsBtn.show(True)
            self.w.clearTasksBtn.show(False)
        else:
            self.w.openPendingsBtn.show(False)
            self.w.copyMDBtn.show(True)
            self.w.clearGlyphsBtn.show(False)
            self.w.clearTasksBtn.show(True)

    def get_master_names(self):
        masters = ["Todas", "Geral"]
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

    def update_counters(self, current_items):
        red_count = sum(1 for item in current_items if item.get("status") == "🔴")
        yellow_count = sum(1 for item in current_items if item.get("status") == "🟡")
        green_count = sum(1 for item in current_items if item.get("status") == "🟢")
        total = len(current_items)

        summary_str = f"Resumo: 🔴 {red_count}  |  🟡 {yellow_count}  |  🟢 {green_count}  (Total: {total})"
        self.counterText.set(summary_str)

    def update_task_counters(self, current_items):
        red_count = sum(1 for item in current_items if item.get("status") == "🔴")
        yellow_count = sum(1 for item in current_items if item.get("status") == "🟡")
        green_count = sum(1 for item in current_items if item.get("status") == "🟢")
        total = len(current_items)

        summary_str = f"Resumo: 🔴 {red_count}  |  🟡 {yellow_count}  |  🟢 {green_count}  (Total: {total})"
        self.taskCounterText.set(summary_str)

    def read_notes_from_ud(self):
        font = Glyphs.font
        if not font:
            return []
        items = []
        for item in font.userData.get("reviewNotes_list", []):
            d = dict(item)
            d["colorIcon"] = self.get_item_color_icon(d)
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
        self.refresh_table_view()

    def filter_notes(self, all_notes):
        font = Glyphs.font
        filtered = list(all_notes)

        selected_master = self.get_active_master_filter()
        if selected_master != "Todas":
            filtered = [item for item in filtered if item.get("master") == selected_master]

        status_idx = self.statusFilterSelect.get()
        if status_idx == 1:
            filtered = [item for item in filtered if item.get("status") == "🔴"]
        elif status_idx == 2:
            filtered = [item for item in filtered if item.get("status") == "🟡"]
        elif status_idx == 3:
            filtered = [item for item in filtered if item.get("status") == "🟢"]

        search_query = self.searchInput.get().strip().lower()
        if search_query:
            filtered = [
                item for item in filtered
                if search_query in item.get("glyph", "").lower() or search_query in item.get("obs", "").lower()
            ]

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
        self.update_counters(filtered)

    def refresh_task_table_view(self):
        font = Glyphs.font
        if not font:
            return
        all_tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])]
        filtered = self.filter_tasks(all_tasks)
        self.taskList.set(filtered)
        self.update_task_counters(filtered)

    def save_data(self, sender=None):
        if self._updating_obs:
            return
        font = Glyphs.font
        if not font:
            return
        self._updating_obs = True
        try:
            current_visible = [dict(t) for t in self.taskList.get()]
            font.userData["reviewNotes_general_tasks"] = current_visible
            self.update_task_counters(current_visible)
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
            target_masters = [m.name for m in font.masters] if font.masters else ["Geral"]
            self.topMasterSelect.set(0)
        else:
            current_active_master = font.selectedFontMaster.name if font.selectedFontMaster else "Geral"
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
                        "master": master_name,
                        "glyph": glyph_name,
                        "obs": ""
                    })

        self.write_notes_to_ud(all_notes)
        self.manualGlyphInput.set("")
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
                v_master = visible_item.get("master", "Geral")
                v_obs = visible_item.get("obs", "")
                v_status = visible_item.get("status", "🔴")

                for global_item in all_notes:
                    if global_item.get("glyph") == v_glyph and global_item.get("master") == v_master:
                        global_item["master"] = v_master
                        global_item["obs"] = v_obs
                        global_item["status"] = v_status

            self.write_notes_to_ud(all_notes)
        finally:
            self._updating_obs = False

    def clear_all_glyphs(self, sender):
        font = Glyphs.font
        if font:
            font.userData["reviewNotes_list"] = []
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

        selected_indexes = self.list.getSelection()
        if not selected_indexes:
            print("Nenhum item selecionado na tabela para abrir.")
            return

        current_list = self.list.get()
        selected_items = [current_list[i] for i in selected_indexes if i < len(current_list)]

        if not selected_items:
            return

        layers_to_open = []
        for item in selected_items:
            glyph_name = item.get("glyph")
            master_name = item.get("master")

            glyph = font.glyphs[glyph_name]
            if not glyph:
                continue

            target_master = None
            if master_name and master_name != "Geral":
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

    def copy_markdown(self, sender):
        font = Glyphs.font
        family_name = font.familyName if font and font.familyName else "Desconhecida"
        file_path = font.filepath if font and font.filepath else "Não salvo"
        file_name = file_path.split("/")[-1] if file_path != "Não salvo" else "Não salvo"
        now_str = datetime.datetime.now().strftime("%d/%m/%Y | %H:%M")

        reviewer = font.userData.get("reviewNotes_reviewer", "") if font else ""
        selected_master = self.get_active_master_filter()
        items = self.read_notes_from_ud()
        
        if selected_master != "Todas":
            items = [item for item in items if item.get("master") == selected_master]

        tasks = [dict(t) for t in font.userData.get("reviewNotes_general_tasks", [])] if font else []

        if not items and not tasks:
            print("Nenhum dado para copiar.")
            return

        md_text = "# Notas\n\n"
        md_text += f"Fonte: {family_name}\n"
        md_text += f"Arquivo: {file_name}\n"
        md_text += f"Data: {now_str}\n"
        if reviewer:
            md_text += f"Última revisão por: {reviewer}\n"
        md_text += "\n"
        md_text += f"## Visualização: {selected_master}\n\n"

        if tasks:
            md_text += "## Tarefas Gerais do Projeto:\n"
            for t in tasks:
                status_icon = t.get('status', '🔴')
                md_text += f"[{status_icon}] {t.get('task', '')}\n"
            md_text += "\n"

        if items:
            md_text += "## Glifos:\n"

            max_master_len = max([len(item.get("master", "")) for item in items] + [len("Master")]) + 4
            max_glyph_len = max([len(item.get("glyph", "")) for item in items] + [len("Glifo")]) + 4

            header = f"{'Status':<10} {'Master':<{max_master_len}} {'Glifo':<{max_glyph_len}} Obs."
            separator = "-" * (len(header) + 20)

            md_text += header + "\n"
            md_text += separator + "\n"

            for item in items:
                status_str = f"[{item.get('status', '🔴')}]"
                master_str = item.get("master", "")
                glyph_str = item.get("glyph", "")
                obs_str = item.get("obs", "")

                md_text += f"{status_str:<10} {master_str:<{max_master_len}} {glyph_str:<{max_glyph_len}} {obs_str}\n"

        pb = NSPasteboard.generalPasteboard()
        pb.declareTypes_owner_([NSStringPboardType], None)
        pb.setString_forType_(md_text, NSStringPboardType)

        print("Relatório copiado com sucesso!")

ReviewNotesFloatingWindow()
