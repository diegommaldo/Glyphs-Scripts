# MenuTitle: Force Kern On Autopairs
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
import vanilla

class KernOnAutoPairUI(object):
    def __init__(self):
        # The default Vietnamese string
        self.viet_string = "điđìđíđỉđĩđịlilìlílỉlĩlịrirìrírỉrĩrịtitìtítỉtĩtịtùtútủtũtỳtỷtỹkỳkỷkỹĐiĐìĐíĐỉĐĩĐịHiHìHíHỉHĩHịKiKìKíKỉKĩKịKyKỳKýKỷKỹKỵTiTìTíTỉTĩTịTùTúTủTũTụTyTỳTýTỷTỹTỵVàVáVảVãVìVíVỉVĩVịVèVéVẻVẽVêVềVếVểVễVòVóVỏVõVọVùVúVủVũVụĂTẮTÂTẤTÊTẾTITÍTÔTỐTƠTỚTƯTỨTĂtẮtÂtẤtÊtẾtItÍtÔtỐtƠtỚtƯtỨtătắtâtấtêtếtitítôtốtơtớtưtứtÔIỒIỐIỔIỖIỘIƠIỜIỚIỞIỠIỢƯIỪIỨIỬIỮIỰIÔiỒiỐiỔiỖiỘiƠiỜiỚiỞiỠiỢiƯiỪiỨiỬiỮiỰiôiồiốiổiỗiộiơiờiớiởiỡiợiưiừiứiửiữiựiƯƠIƯƠNƯMƯNƠMƠNƯơiƯơnƯmƯnƠmƠnươiươnưmưnưaơmơnYêYềYếYểYễYệ"
        
        window_width = 400
        window_height = 340
        self.w = vanilla.FloatingWindow(
            (window_width, window_height), "Kern On Force Autopairs Tool"
        )

        # 1. Instructions at the top
        instructions = "1. Paste text or click 'Viet Glyphs'\n2. Select 'All Masters' if not, just open master\n3. Click 'Auto-Pair!'"
        self.w.instructionText = vanilla.TextBox((15, 15, -15, 60), instructions, sizeStyle='small')
        
        # 2. Text Editor for custom strings
        self.w.textTitle = vanilla.TextBox((15, 80, -15, 17), "Text to process:", sizeStyle='small')
        self.w.inputText = vanilla.TextEditor((15, 100, -15, 100), "")
        
        # 3. Button to load the Vietnamese string
        self.w.loadVietBtn = vanilla.Button((15, 210, 150, 20), "Viet Glyphs", callback=self.load_viet_glyphs, sizeStyle='small')
        
        # 4. Checkbox for All Masters
        self.w.allMasters = vanilla.CheckBox((15, 245, -15, 20), "Apply to all masters", value=False)
        
        # 5. Action Button
        self.w.runButton = vanilla.Button((15, 280, -15, 40), "Auto-Pair!", callback=self.run_logic)

        self.w.open()

    def load_viet_glyphs(self, sender):
        self.w.inputText.set(self.viet_string)

    def run_logic(self, sender):
        thisFont = Glyphs.font
        if not thisFont:
            return

        raw_text = self.w.inputText.get()
        full_clean_text = "".join(raw_text.split())
        
        if not full_clean_text:
            print("⚠️ Please enter some text or click 'Viet Glyphs' first.")
            return

        if self.w.allMasters.get():
            masters_to_process = thisFont.masters
        else:
            masters_to_process = [thisFont.selectedFontMaster]

        auto_key = "KernOnUserSetAutopairs"
        indie_key = "KernOnIndependentPairs"
        total_added = 0
        
        for master in masters_to_process:
            # We must use list() to ensure we are editing a copy, then re-save it
            current_autopairs = list(master.userData[auto_key]) if master.userData[auto_key] else []
            current_indiepairs = list(master.userData[indie_key]) if master.userData[indie_key] else []
            
            added_this_master = 0
            
            for i in range(len(full_clean_text) - 1):
                l_char, r_char = full_clean_text[i], full_clean_text[i+1]
                l_g = thisFont.glyphForCharacter_(ord(l_char))
                r_g = thisFont.glyphForCharacter_(ord(r_char))
                
                if l_g and r_g:
                    pair = "%s %s" % (l_g.name, r_g.name)
                    
                    if pair not in current_autopairs:
                        current_autopairs.append(pair)
                        added_this_master += 1
                    
                    if pair in current_indiepairs:
                        current_indiepairs.remove(pair)

            master.userData[auto_key] = current_autopairs
            master.userData[indie_key] = current_indiepairs
            total_added += added_this_master

        # Finalize by opening a tab and notifying Glyphs
        thisFont.newTab(full_clean_text)
        thisFont.parent.windowControllers()[0].document().updateChangeCount_(0)
        
        print("\n✅ Processed %d master(s)." % len(masters_to_process))
        print("✅ Added %d new transitions to Kern On Auto-pairs." % total_added)
        print("✅ Edit tab opened. Ensure Kern On is re-opened to see results.")

KernOnAutoPairUI()