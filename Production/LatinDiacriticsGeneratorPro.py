# MenuTitle: Latin Diacritics Glyph Generator Pro
# encoding: utf-8

import vanilla
from GlyphsApp import Glyphs, GSGlyph, GSComponent

# 0. Clear Macro Panel Log
Glyphs.clearLog()

class DiacriticsGeneratorInterface(object):
    def __init__(self):
        # Structured window with optimized dimensions (420x760)
        self.w = vanilla.FloatingWindow((420, 760), "Latin Diacritics Glyph Generator Pro")
        
        # --- TAB SELECTOR VIA SEGMENTED BUTTON ---
        tab_desc = [{"title": "Settings"}, {"title": "Diacritics"}]
        self.w.tab_selector = vanilla.SegmentedButton(
            (15, 10, -15, 24),
            segmentDescriptions=tab_desc,
            callback=self.switch_tab
        )
        self.w.tab_selector.set(0)
        
        # =========================================================================
        # GROUP 1: SETTINGS (Tab 0)
        # =========================================================================
        self.w.group_tab0 = vanilla.Group((0, 40, -0, 700))
        g1 = self.w.group_tab0
        
        # Section 1: Scope
        g1.scope_label = vanilla.TextBox((15, 5, -15, 20), "Analyze base letters in:")
        g1.scope_choice = vanilla.RadioGroup((15, 28, -15, 45), 
                                               ["Selected glyphs only", "All glyphs in font"],
                                               isVertical=True)
        g1.scope_choice.set(1) # Default to all glyphs
        
        g1.divider_1 = vanilla.HorizontalLine((15, 85, -15, 1))
        
        # Section 2: Cases
        g1.case_label = vanilla.TextBox((15, 98, -15, 20), "Affected cases:")
        g1.generate_uppercase = vanilla.CheckBox((15, 122, 110, 20), "Uppercase", value=True)
        g1.generate_lowercase = vanilla.CheckBox((135, 122, 110, 20), "Lowercase", value=True)
        g1.generate_smallcaps = vanilla.CheckBox((250, 122, 110, 20), "Small Caps", value=False)
        
        g1.divider_2 = vanilla.HorizontalLine((15, 155, -15, 1))
        
        # Section 3: Combining Marks
        g1.comb_label = vanilla.TextBox((15, 168, -15, 20), "Combining marks (*comb):")
        g1.generate_comb = vanilla.CheckBox((15, 192, -15, 20), "Generate missing combining marks", value=True)
        g1.generate_comb_case = vanilla.CheckBox((35, 216, -15, 20), "Include case marks (.case)", value=True)
        g1.generate_comb_narrow = vanilla.CheckBox((35, 240, -15, 20), "Include narrow marks (.narrow)", value=True)
        
        g1.divider_3 = vanilla.HorizontalLine((15, 273, -15, 1))
        
        # Section 4: Additional Options
        g1.options_label = vanilla.TextBox((15, 286, -15, 20), "Additional generation options:")
        g1.ignore_ligatures = vanilla.CheckBox((15, 310, 160, 20), "Ignore ligatures", value=True)
        g1.ignore_non_exporting = vanilla.CheckBox((180, 310, 170, 20), "Ignore non-exporting", value=True)
        
        g1.include_alternates = vanilla.CheckBox((15, 334, 160, 20), "Include alts (.ss01...)", value=False)
        g1.regenerate_existing = vanilla.CheckBox((15, 358, 160, 20), "Overwrite existing", value=False)
        g1.open_tab = vanilla.CheckBox((180, 358, 170, 20), "🔠 Open in new tab", value=False)

        # =========================================================================
        # GROUP 2: DIACRITICS (Tab 1)
        # =========================================================================
        self.w.group_tab1 = vanilla.Group((0, 40, -0, 700))
        g2 = self.w.group_tab1
        
        # --- LANGUAGES / REGIONS (2 COLUMNS) ---
        g2.languages_label = vanilla.TextBox((15, 5, -15, 20), "Languages / Regions:")
        
        g2.region_portuguese = vanilla.CheckBox((15, 27, 110, 20), "Portuguese", value=True, callback=self.region_checkbox_event)
        g2.num_portuguese = vanilla.TextBox((125, 29, 60, 16), "14", sizeStyle="small")

        g2.region_se_euro = vanilla.CheckBox((15, 50, 110, 20), "SE European", value=False, callback=self.region_checkbox_event)
        g2.num_se_euro = vanilla.TextBox((125, 52, 60, 16), "66", sizeStyle="small")

        g2.region_central = vanilla.CheckBox((15, 73, 110, 20), "Central Euro", value=False, callback=self.region_checkbox_event)
        g2.num_central = vanilla.TextBox((125, 75, 60, 16), "133", sizeStyle="small")

        g2.region_western = vanilla.CheckBox((215, 27, 110, 20), "Western Euro", value=False, callback=self.region_checkbox_event)
        g2.num_western = vanilla.TextBox((325, 29, 60, 16), "33", sizeStyle="small")

        g2.region_vietnam = vanilla.CheckBox((215, 50, 110, 20), "Vietnamese", value=False, callback=self.region_checkbox_event)
        g2.num_vietnam = vanilla.TextBox((325, 52, 60, 16), "134", sizeStyle="small")

        g2.region_all = vanilla.CheckBox((215, 73, 110, 20), "All Possible", value=False, callback=self.region_checkbox_event)
        g2.num_all = vanilla.TextBox((325, 75, 60, 16), "310", sizeStyle="small")
        
        g2.divider_1 = vanilla.HorizontalLine((15, 99, -15, 1))

        # --- STANDARDS (2 COLUMNS) ---
        g2.sub_gf = vanilla.TextBox((15, 107, -15, 16), "GOOGLE FONTS", sizeStyle="small")
        
        g2.region_gf_core = vanilla.CheckBox((15, 125, 110, 20), "GF Core", value=False, callback=self.region_checkbox_event)
        g2.num_gf_core = vanilla.TextBox((125, 127, 60, 16), "42", sizeStyle="small")

        g2.region_gf_plus = vanilla.CheckBox((215, 125, 110, 20), "GF Plus", value=False, callback=self.region_checkbox_event)
        g2.num_gf_plus = vanilla.TextBox((325, 127, 60, 16), "192", sizeStyle="small")

        g2.region_gf_pro = vanilla.CheckBox((15, 147, 110, 20), "GF Pro", value=False, callback=self.region_checkbox_event)
        g2.num_gf_pro = vanilla.TextBox((125, 149, 60, 16), "195", sizeStyle="small")

        g2.region_gf_pro_unique = vanilla.CheckBox((215, 147, 110, 20), "GF Pro Unique", value=False, callback=self.region_checkbox_event)
        g2.num_gf_pro_unique = vanilla.TextBox((325, 147, 60, 16), "17", sizeStyle="small")
        
        g2.sub_koeberlin = vanilla.TextBox((15, 173, -15, 16), "KOEBERLIN", sizeStyle="small")
        
        g2.region_koeberlin_s = vanilla.CheckBox((15, 191, 110, 20), "Koeberlin S", value=False, callback=self.region_checkbox_event)
        g2.num_k_s = vanilla.TextBox((125, 193, 60, 16), "43", sizeStyle="small")

        g2.region_koeberlin_m = vanilla.CheckBox((215, 191, 110, 20), "Koeberlin M", value=False, callback=self.region_checkbox_event)
        g2.num_k_m = vanilla.TextBox((325, 193, 60, 16), "109", sizeStyle="small")

        g2.region_koeberlin_l = vanilla.CheckBox((15, 213, 110, 20), "Koeberlin L", value=False, callback=self.region_checkbox_event)
        g2.num_k_l = vanilla.TextBox((125, 215, 60, 16), "237", sizeStyle="small")

        g2.region_koeberlin_xl = vanilla.CheckBox((215, 213, 110, 20), "Koeberlin XL", value=False, callback=self.region_checkbox_event)
        g2.num_k_xl = vanilla.TextBox((325, 215, 60, 16), "237", sizeStyle="small")
        
        g2.sub_underware = vanilla.TextBox((15, 239, -15, 16), "UNDERWARE", sizeStyle="small")
        g2.region_underware = vanilla.CheckBox((15, 257, 110, 20), "Underware", value=False, callback=self.region_checkbox_event)
        g2.num_underware = vanilla.TextBox((125, 259, 60, 16), "129", sizeStyle="small")

        g2.sub_adobe = vanilla.TextBox((215, 239, -15, 16), "ADOBE", sizeStyle="small")
        g2.region_glyph_list_2 = vanilla.CheckBox((215, 257, 110, 20), "Glyph List 2.0", value=False, callback=self.region_checkbox_event)
        g2.num_adobe = vanilla.TextBox((325, 259, 60, 16), "310", sizeStyle="small")
        
        g2.divider_region = vanilla.HorizontalLine((15, 283, -15, 1))
        
        # --- DIACRITICS CHECKBOXES & CONTROLS ---
        g2.instruction = vanilla.TextBox((15, 293, 140, 20), "Active diacritics:")
        g2.uncheck_button = vanilla.Button((200, 291, 90, 22), "None", callback=self.uncheck_all_diacritics)
        g2.check_button = vanilla.Button((300, 291, 90, 22), "All", callback=self.check_all_diacritics)
        
        # Diacritics Checkboxes
        g2.acc_acute = vanilla.CheckBox((15, 321, 120, 20), "Acute", value=True)
        g2.acc_grave = vanilla.CheckBox((15, 344, 120, 20), "Grave", value=True)
        g2.acc_dieresis = vanilla.CheckBox((15, 367, 120, 20), "Dieresis", value=False)
        g2.acc_circumflex = vanilla.CheckBox((15, 390, 120, 20), "Circumflex", value=True)
        g2.acc_tilde = vanilla.CheckBox((15, 413, 120, 20), "Tilde", value=True)
        g2.acc_hookabove = vanilla.CheckBox((15, 436, 120, 20), "Hook Above", value=False)
        g2.acc_horn = vanilla.CheckBox((15, 459, 120, 20), "Horn", value=False)
        g2.acc_dotaccent = vanilla.CheckBox((15, 482, 120, 20), "Dot Above", value=False)
        g2.acc_hungarumlaut = vanilla.CheckBox((15, 505, 120, 20), "Hungarumlaut", value=False)

        g2.acc_cedilla = vanilla.CheckBox((145, 321, 120, 20), "Cedilla", value=True)
        g2.acc_macron = vanilla.CheckBox((145, 344, 120, 20), "Macron", value=False)
        g2.acc_macronbelow = vanilla.CheckBox((145, 367, 120, 20), "Macron Below", value=False)
        g2.acc_breve = vanilla.CheckBox((145, 390, 120, 20), "Breve", value=False)
        g2.acc_brevebelow = vanilla.CheckBox((145, 413, 120, 20), "Breve Below", value=False)
        g2.acc_ring = vanilla.CheckBox((145, 436, 120, 20), "Ring Above", value=False)
        g2.acc_caron = vanilla.CheckBox((145, 459, 120, 20), "Caron", value=False)
        g2.acc_dotbelow = vanilla.CheckBox((145, 482, 120, 20), "Dot Below", value=False)
        g2.acc_ogonek = vanilla.CheckBox((145, 505, 120, 20), "Ogonek", value=False)

        g2.acc_commaaccent = vanilla.CheckBox((275, 321, 120, 20), "Comma Below", value=False)
        g2.acc_commaturnedabove = vanilla.CheckBox((275, 344, 120, 20), "Comma Above", value=False)
        g2.acc_dblgrave = vanilla.CheckBox((275, 367, 120, 20), "Double Grave", value=False)
        g2.acc_invertedbreve = vanilla.CheckBox((275, 390, 120, 20), "Inverted Breve", value=False)

        self.diacritics_map = {
            "acute": g2.acc_acute, "grave": g2.acc_grave, "dieresis": g2.acc_dieresis,
            "circumflex": g2.acc_circumflex, "tilde": g2.acc_tilde, "hookabove": g2.acc_hookabove,
            "horn": g2.acc_horn, "dotaccent": g2.acc_dotaccent, "hungarumlaut": g2.acc_hungarumlaut,
            "cedilla": g2.acc_cedilla, "macron": g2.acc_macron, "macronbelow": g2.acc_macronbelow,
            "breve": g2.acc_breve, "brevebelow": g2.acc_brevebelow, "ring": g2.acc_ring, 
            "caron": g2.acc_caron, "dotbelow": g2.acc_dotbelow, "ogonek": g2.acc_ogonek, 
            "commaaccent": g2.acc_commaaccent, "commaturnedabove": g2.acc_commaturnedabove, 
            "dblgrave": g2.acc_dblgrave, "invertedbreve": g2.acc_invertedbreve
        }
        self.diacritics_list = list(self.diacritics_map.keys())

        g2.show(False)

        # --- PROGRESS BAR AND STATUS (Fixed at Footer) ---
        self.w.progress_bar = vanilla.ProgressBar((15, 650, -15, 12))
        self.w.progress_bar.set(0)
        self.w.status_text = vanilla.TextBox((15, 666, -15, 18), "Waiting to start...", sizeStyle="small")

        # Main Button
        self.w.run_button = vanilla.Button((15, 693, -15, 35), "Generate Accented Glyphs", callback=self.generate_diacritics)
        
        # Legal Diacritics Mapping
        self.legal_map = {
            "portugues": {
                "acute": ["a", "e", "i", "o", "u"], "grave": ["a"], "circumflex": ["a", "e", "o"],
                "tilde": ["a", "o"], "cedilla": ["c"]
            },
            "western": {
                "acute": ["a", "e", "i", "o", "u", "y", "j"], "grave": ["a", "e", "i", "o", "u"],
                "dieresis": ["a", "e", "i", "o", "u", "y"], "circumflex": ["a", "e", "i", "o", "u"],
                "tilde": ["a", "n", "o"], "cedilla": ["c"], "ring": ["a"]
            },
            "central": {
                "acute": ["a", "c", "e", "i", "l", "n", "o", "r", "s", "u", "y", "z"],
                "dieresis": ["a", "e", "i", "o", "u", "y"], "circumflex": ["a", "e", "i", "o", "u"],
                "cedilla": ["c", "s", "t"], "macron": ["a", "e", "i", "o", "u"],
                "macronbelow": ["a", "e", "i", "o", "u", "b", "d", "h", "k", "l", "n", "r", "t", "z"], 
                "breve": ["a", "e", "g", "u"], "brevebelow": ["h"],
                "ring": ["a", "u"], "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z"],
                "ogonek": ["a", "e", "i", "u"], "dotaccent": ["z"], "hungarumlaut": ["o", "u"]
            },
            "se_euro": {
                "acute": ["a", "e", "i", "o", "u", "g", "k", "l", "n", "r", "s", "z"],
                "grave": ["a", "e", "i", "o", "u"], "dieresis": ["a", "e", "i", "o", "u"],
                "circumflex": ["a", "e", "i", "o", "u", "c", "g", "h", "j", "s", "w", "y"],
                "cedilla": ["c", "g", "k", "l", "n", "r", "s", "t"], "breve": ["a", "e", "g", "u"],
                "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z"], "commaaccent": ["s", "t"]
            },
            "vietnam": {
                "acute": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "grave": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "circumflex": ["a", "e", "o"],
                "tilde": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "hookabove": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "horn": ["o", "u"], "breve": ["a"],
                "dotbelow": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "circumflex_acute": ["a", "e", "o"],
                "circumflex_grave": ["a", "e", "o"],
                "circumflex_hookabove": ["a", "e", "o"],
                "circumflex_tilde": ["a", "e", "o"],
                "breve_acute": ["a"],
                "breve_grave": ["a"],
                "breve_hookabove": ["a"],
                "breve_tilde": ["a"]
            },
            "gf_core": {
                "acute": ["u", "y", "a", "e", "i", "o"], "circumflex": ["u", "a", "e", "i", "o"],
                "dieresis": ["u", "a", "e", "i", "o", "y"], "grave": ["u", "a", "e", "i", "o"],
                "ring": ["a"], "tilde": ["a", "o", "n"], "cedilla": ["c"]
            },
            "gf_plus": {
                "acute": ["u", "y", "a", "e", "i", "o", "c", "g", "k", "l", "n", "r", "s", "z", "w", "ohorn", "uhorn", "aring", "ae", "emacron", "omacron", "otilde", "utilde", "dcroat"],
                "grave": ["u", "a", "e", "i", "o", "w", "y", "ohorn", "uhorn"],
                "circumflex": ["u", "a", "e", "i", "o", "c", "g", "h", "j", "s", "w", "y", "z"],
                "dieresis": ["u", "a", "e", "i", "o", "y", "w"],
                "ring": ["a", "u"], 
                "tilde": ["a", "o", "i", "n", "u", "y", "ohorn", "uhorn", "etilde"],
                "cedilla": ["c", "s", "t"], "breve": ["a", "e", "g", "i", "o", "u"],
                "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z", "g", "k", "o", "u", "dz", "j"],
                "dotaccent": ["c", "e", "g", "i", "z"], 
                "dotbelow": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "hookabove": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "horn": ["o", "u"], "hungarumlaut": ["o", "u"], "macron": ["a", "e", "i", "o", "u", "y"],
                "ogonek": ["a", "e", "i", "u", "o"], "commaaccent": ["g", "k", "l", "n", "r", "s", "t"],
                "dblgrave": ["a", "e", "i", "o", "r", "u"], "invertedbreve": ["a", "e", "i", "o", "r", "u"],
                "breve_acute": ["a", "e", "o", "u"],
                "breve_grave": ["a", "e", "o", "u"],
                "breve_hookabove": ["a", "e", "o", "u"],
                "breve_tilde": ["a", "e", "o", "u"],
                "circumflex_acute": ["a", "e", "o", "u"],
                "circumflex_grave": ["a", "e", "o", "u"],
                "circumflex_hookabove": ["a", "e", "o", "u"],
                "circumflex_tilde": ["a", "e", "o", "u"]
            },
            "gf_pro": {
                "acute": ["u", "y", "a", "e", "i", "o", "c", "g", "k", "l", "n", "r", "s", "z", "w", "ohorn", "uhorn", "aring", "ae", "emacron", "omacron", "otilde", "utilde", "idieresis", "ccedilla"],
                "circumflex": ["u", "a", "e", "i", "o", "c", "g", "h", "j", "s", "w", "y", "z"],
                "dieresis": ["u", "a", "e", "i", "o", "y", "w", "otilde", "umacron", "t"],
                "grave": ["u", "a", "e", "i", "o", "w", "y", "ohorn", "uhorn", "emacron", "omacron"],
                "ring": ["a", "u"], "tilde": ["a", "o", "i", "n", "u", "y", "ohorn", "uhorn"],
                "cedilla": ["c", "s", "t", "e"], "breve": ["a", "e", "g", "i", "o", "u"], "brevebelow": ["h"],
                "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z", "g", "k", "o", "u", "dz", "j"],
                "dotaccent": ["c", "e", "g", "i", "z", "n", "s", "y"],
                "dotbelow": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn", "d", "h", "l", "m", "n", "r", "s", "t", "z"],
                "hookabove": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "horn": ["o", "u"], "hungarumlaut": ["o", "u"],
                "macron": ["a", "e", "i", "o", "u", "y", "g", "umacron"],
                "macronbelow": ["d", "l", "n", "r", "t"], "ogonek": ["a", "e", "i", "u", "o"],
                "commaaccent": ["g", "k", "l", "n", "r", "s", "t"], "dblgrave": ["a", "e", "i", "o", "r", "u"],
                "invertedbreve": ["a", "e", "i", "o", "r", "u"],
                "breve_acute": ["a", "e", "o", "u"],
                "breve_grave": ["a", "e", "o", "u"],
                "breve_hookabove": ["a", "e", "o", "u"],
                "breve_tilde": ["a", "e", "o", "u"],
                "circumflex_acute": ["a", "e", "o", "u"],
                "circumflex_grave": ["a", "e", "o", "u"],
                "circumflex_hookabove": ["a", "e", "o", "u"],
                "circumflex_tilde": ["a", "e", "o", "u"]
            },
            "gf_pro_unique": {
                "acute": ["ccedilla", "emacron", "idieresis", "otilde", "omacron", "utilde"],
                "grave": ["emacron", "omacron"],
                "dieresis": ["otilde", "umacron", "t"],
                "breve": ["ecedilla"],
                "dotaccent": ["sacute", "scaron", "sdotbelow"]
            },
            "glyph_list_2": {
                "acute": [
                    "a", "ae", "aring", "c", "ccedilla", "e", "emacron", 
                    "edieresis", "edot", "g", "h", "i", "idieresis", "k", "l", "m", "n", "o", "omacron", 
                    "odieresis", "ohorn", "otilde", "p", "r", "s", "u", "umacron", 
                    "udieresis", "uhorn", "utilde", "v", "w", "y", "ydieresis", "z"
                ],
                "grave": [
                    "a", "e", "emacron", "i", "o", "omacron", "ohorn", "u", "w", "y"
                ],
                "dieresis": [
                    "a", "e", "h", "i", "otilde", "t", "u", "umacron", "w", 
                    "x", "y", "z"
                ],
                "circumflex": [
                    "a", "c", "e", "g", "h", "i", "j", "l", "n", "o", "s", "u", "w", 
                    "y", "z"
                ],
                "tilde": [
                    "a", "e", "i", "n", "o", "ohorn", "u", "uhorn", "utilde", "v", "y"
                ],
                "hookabove": [
                    "a", "e", "i", "o", "ohorn", "u", "uhorn", "y"
                ],
                "horn": ["o", "u"],
                "dotaccent": [
                    "b", "c", "d", "e", "f", "g", 
                    "h", "i", "l", "m", "n", "o", "p", 
                    "r", "s", "t", "w", 
                    "x", "y", "z"
                ],
                "hungarumlaut": ["o", "u"],
                "cedilla": ["c", "d", "e", "g", "h", "k", "l", "n", "r", "s", "t"],
                "macron": [
                    "a", "ae", "d", "e", "g", "i", "l", 
                    "o", "u", "y"
                ],
                "macronbelow": [
                    "a", "b", "d", "e", "h", "k", "l", "n", "r", "t", "z"
                ],
                "breve": [
                    "a", "e", "g", "i", "o", "u"
                ],
                "brevebelow": ["h"],
                "ring": [
                    "a", "u", "w", "y"
                ],
                "caron": [
                    "a", "c", "d", "dzcaron", "e", "ezhcaron", "g", 
                    "h", "i", "k", "l", "n", "o", "r", 
                    "s", "t", "u", "z"
                ],
                "dotbelow": [
                    "a", "b", "d", "e", 
                    "h", "i", "k", "l", 
                    "m", "n", "o", "ohorn", "r", "s", 
                    "t", "u", "uhorn", "v", "w", 
                    "y", "z"
                ],
                "ogonek": ["a", "e", "i", "o", "u"],
                "commaaccent": ["g", "k", "l", "n", "r", "s", "t"],
                "commaturnedabove": ["a", "e", "i", "o", "u"],
                "dblgrave": ["a", "e", "i", "o", "r", "u"],
                "invertedbreve": ["a", "e", "i", "o", "r", "u"],
                "breve_acute": ["a", "e", "o", "u"],
                "breve_grave": ["a", "e", "o", "u"],
                "breve_hookabove": ["a", "e", "o", "u"],
                "breve_tilde": ["a", "e", "o", "u"],
                "circumflex_acute": ["a", "e", "o", "u"],
                "circumflex_grave": ["a", "e", "o", "u"],
                "circumflex_hookabove": ["a", "e", "o", "u"],
                "circumflex_tilde": ["a", "e", "o", "u"]
            },
            "koeberlin_s": {
                "acute": ["a", "e", "i", "o", "u", "y"], "grave": ["a", "e", "i", "o", "u"],
                "dieresis": ["a", "e", "i", "o", "u", "y", "h"], "circumflex": ["a", "e", "i", "o", "u"],
                "tilde": ["a", "n", "o"], "cedilla": ["c"]
            },
            "koeberlin_m": {
                "acute": ["a", "c", "e", "i", "l", "n", "o", "r", "s", "u", "y", "z", "ohorn", "uhorn"],
                "grave": ["a", "e", "i", "o", "u", "ohorn", "uhorn"], 
                "dieresis": ["a", "e", "i", "o", "u", "y", "h"],
                "circumflex": ["a", "e", "i", "o", "u", "c", "g", "h", "j", "s", "w", "y"],
                "tilde": ["a", "n", "o", "ohorn", "uhorn"], 
                "hookabove": ["ohorn", "uhorn"],
                "cedilla": ["c", "s", "t"], 
                "macron": ["a", "e", "i", "o", "u", "ae"],
                "macronbelow": ["a", "e", "i", "o", "u", "b", "d", "h", "k", "l", "n", "r", "t", "z"],
                "breve": ["a", "e", "g", "u"], "brevebelow": ["h"], "ring": ["a", "u"],
                "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z"], "ogonek": ["a", "e", "i", "u"],
                "dotaccent": ["c", "e", "g", "i", "z"], "hungarumlaut": ["o", "u"],
                "commaturnedabove": ["a", "e", "i", "o", "u"], 
                "dotbelow": ["l", "r", "ohorn", "uhorn"]
            },
            "koeberlin_l": {
                "acute": ["a", "c", "e", "i", "k", "l", "m", "n", "o", "p", "r", "s", "u", "w", "y", "z", "aring", "ccedilla", "emacron", "omacron", "otilde", "utilde", "ae", "ohorn", "uhorn", "g", "idieresis", "oogonek", "oslash"],
                "grave": ["a", "e", "i", "o", "u", "w", "y", "emacron", "omacron", "ohorn", "uhorn", "n"], 
                "dieresis": ["a", "e", "i", "o", "u", "w", "x", "y", "t", "otilde"],
                "circumflex": ["a", "c", "e", "g", "h", "i", "j", "o", "s", "u", "w", "y", "z"],
                "tilde": ["a", "e", "i", "n", "o", "u", "v", "y", "ohorn", "uhorn"], 
                "hookabove": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "horn": ["o", "u"], "cedilla": ["c", "e", "g", "h", "k", "l", "n", "r", "s", "t", "d"],
                "macron": ["a", "e", "g", "i", "o", "u", "y", "ae"], 
                "macronbelow": ["a", "e", "i", "o", "u", "b", "d", "h", "k", "l", "n", "r", "t", "z"],
                "breve": ["a", "e", "g", "i", "o", "u"], "brevebelow": ["h"], "ring": ["a", "u", "w", "y"],
                "caron": ["a", "c", "d", "e", "g", "h", "i", "k", "l", "n", "o", "r", "s", "t", "u", "z", "dz", "ezh", "j"],
                "dotbelow": ["a", "b", "d", "e", "h", "i", "k", "l", "m", "n", "o", "r", "s", "t", "u", "v", "w", "y", "z", "aring", "ohorn", "uhorn"],
                "ogonek": ["a", "e", "i", "o", "u"], 
                "dotaccent": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "l", "m", "n", "o", "p", "r", "s", "t", "w", "x", "y", "z", "longs"],
                "commaaccent": ["k", "l", "n", "r", "s", "t"], "hungarumlaut": ["o", "u"], "dblgrave": ["a", "e", "i", "o", "r", "u"],
                "invertedbreve": ["a", "e", "i", "o", "r", "u"],
                "breve_acute": ["a", "e", "o", "u"],
                "breve_grave": ["a", "e", "o", "u"],
                "breve_hookabove": ["a", "e", "o", "u"],
                "breve_tilde": ["a", "e", "o", "u"],
                "circumflex_acute": ["a", "e", "o", "u"],
                "circumflex_grave": ["a", "e", "o", "u"],
                "circumflex_hookabove": ["a", "e", "o", "u"],
                "circumflex_tilde": ["a", "e", "o", "u"]
            },
            "underware": {
                "acute": ["a", "c", "e", "i", "l", "n", "o", "r", "s", "u", "y", "z"],
                "grave": ["a", "e", "i", "o", "u"], "dieresis": ["a", "e", "i", "o", "u", "y"],
                "circumflex": ["a", "c", "e", "g", "h", "i", "j", "o", "s", "u", "w", "y"],
                "tilde": ["a", "i", "n", "o", "u"], "cedilla": ["c", "g", "k", "l", "n", "r", "s", "t"],
                "macron": ["a", "e", "i", "o", "u"], "breve": ["a", "e", "g", "i", "o", "u"],
                "ring": ["a", "u"], "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z"],
                "ogonek": ["a", "e", "i", "u"], "dotaccent": ["c", "e", "g", "i", "z"],
                "commaaccent": ["s", "t"], "hungarumlaut": ["o", "u"]
            },
            "todos": {
                "acute": ["a", "e", "i", "o", "u", "y", "c", "g", "k", "l", "n", "r", "s", "z", "j", "m", "p", "w", "aring", "ccedilla", "emacron", "omacron", "otilde", "utilde", "ae", "ohorn", "uhorn", "idieresis", "oogonek", "oslash"],
                "grave": ["a", "e", "i", "o", "u", "w", "y", "emacron", "omacron", "ohorn", "uhorn", "n"], 
                "dieresis": ["a", "e", "i", "o", "u", "y", "w", "x", "h", "t", "otilde"],
                "circumflex": ["a", "e", "i", "o", "u", "c", "g", "h", "j", "s", "w", "y", "z"],
                "tilde": ["a", "e", "i", "o", "u", "y", "n", "v", "ohorn", "uhorn"], 
                "hookabove": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn"],
                "horn": ["o", "u"], "cedilla": ["c", "g", "k", "l", "n", "r", "s", "t", "e", "h", "d"],
                "macron": ["a", "e", "i", "o", "u", "g", "y", "ae"], 
                "macronbelow": ["a", "e", "i", "o", "u", "b", "d", "h", "k", "l", "n", "r", "t", "z"],
                "breve": ["a", "e", "g", "i", "o", "u"], "brevebelow": ["h"], "ring": ["a", "u", "w", "y"],
                "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z", "a", "g", "h", "i", "k", "o", "u", "dz", "ezh", "j"],
                "dotbelow": ["a", "b", "d", "e", "h", "i", "k", "l", "m", "n", "o", "r", "s", "t", "u", "v", "w", "y", "z", "aring", "ohorn", "uhorn"],
                "ogonek": ["a", "e", "i", "o", "u"], "dotaccent": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "l", "m", "n", "o", "p", "r", "s", "t", "w", "x", "y", "z", "longs"],
                "commaaccent": ["k", "l", "n", "r", "s", "t"], "commaturnedabove": ["a", "e", "i", "o", "u"], "hungarumlaut": ["o", "u"], "dblgrave": ["a", "e", "i", "o", "r", "u"],
                "invertedbreve": ["a", "e", "i", "o", "r", "u"],
                "breve_acute": ["a", "e", "o", "u"],
                "breve_grave": ["a", "e", "o", "u"],
                "breve_hookabove": ["a", "e", "o", "u"],
                "breve_tilde": ["a", "e", "o", "u"],
                "circumflex_acute": ["a", "e", "o", "u"],
                "circumflex_grave": ["a", "e", "o", "u"],
                "circumflex_hookabove": ["a", "e", "o", "u"],
                "circumflex_tilde": ["a", "e", "o", "u"]
            }
        }
        self.legal_map["koeberlin_xl"] = self.legal_map["koeberlin_l"]
        
        self.double_keys = {
            "breve_acute": "brevecomb_acutecomb", "breve_grave": "brevecomb_gravecomb",
            "breve_hookabove": "brevecomb_hookabovecomb", "breve_tilde": "brevecomb_tildecomb",
            "circumflex_acute": "circumflexcomb_acutecomb", "circumflex_grave": "circumflexcomb_gravecomb",
            "circumflex_hookabove": "circumflexcomb_hookabovecomb", "circumflex_tilde": "circumflexcomb_tildecomb"
        }
        
        self.combining_cache = {}
        self.common_ligatures = set(["ff", "fi", "fl", "ffi", "ffl", "ft", "st", "ct", "fb", "fh", "fj", "fk", "fr", "fs"])
        self.dotless_map = {"i": "idotless", "j": "jdotless"}

        self.fallback_composite_bases = set([
            "abreve", "acircumflex", "ecircumflex", "ocircumflex",
            "ohorn", "uhorn", "emacron", "omacron", "otilde",
            "utilde", "idieresis", "udieresis", "aring",
            "aacute", "agrave", "adieresis", "atilde", "aogonek", "amacron",
            "ccedilla", "ccaron", "cacute",
            "dcaron", "eacute", "egrave", "edieresis", "ecaron", "eogonek",
            "ebreve", "etilde",
            "gbreve", "gcommaaccent", "hcircumflex",
            "iacute", "igrave", "iogonek", "imacron", "ibreve", "itilde",
            "jcircumflex", "kcommaaccent",
            "lacute", "lcaron", "ldot", "lcommaaccent",
            "nacute", "ncaron", "ntilde", "ncommaaccent",
            "oacute", "ograve", "odieresis", "ohungarumlaut", "oslashacute",
            "racute", "rcaron", "rcommaaccent",
            "sacute", "scircumflex", "scedilla", "scaron",
            "tcaron", "tcommaaccent",
            "uacute", "ugrave", "ucircumflex", "uring", "uhungarumlaut",
            "uogonek", "ubreve",
            "wcircumflex", "wacute", "wgrave", "wdieresis",
            "yacute", "ycircumflex", "ydieresis", "ygrave",
            "zacute", "zdotaccent", "zcaron"
        ])
        
        self.region_checkbox_event(None)
        self.w.open()

    def switch_tab(self, sender):
        index = sender.get()
        self.w.group_tab0.show(index == 0)
        self.w.group_tab1.show(index == 1)

    def uncheck_all_diacritics(self, sender):
        for checkbox in self.diacritics_map.values():
            checkbox.set(False)

    def check_all_diacritics(self, sender):
        for checkbox in self.diacritics_map.values():
            checkbox.set(True)

    def region_checkbox_event(self, sender):
        g2 = self.w.group_tab1
        standards_map = {
            "gf_core": g2.region_gf_core, "gf_plus": g2.region_gf_plus,
            "gf_pro": g2.region_gf_pro, "gf_pro_unique": g2.region_gf_pro_unique,
            "glyph_list_2": g2.region_glyph_list_2, "koeberlin_s": g2.region_koeberlin_s,
            "koeberlin_m": g2.region_koeberlin_m, "koeberlin_l": g2.region_koeberlin_l,
            "koeberlin_xl": g2.region_koeberlin_xl, "underware": g2.region_underware
        }
        
        if sender in standards_map.values() and sender.get() == True:
            g2.region_portuguese.set(False)
            g2.region_western.set(False)
            g2.region_central.set(False)
            g2.region_se_euro.set(False)
            g2.region_vietnam.set(False)
            g2.region_all.set(False)
        
        region_definitions = {
            "portugues": ["acute", "grave", "circumflex", "tilde", "cedilla"],
            "western": ["acute", "grave", "dieresis", "circumflex", "tilde", "cedilla", "ring"],
            "central": ["acute", "dieresis", "circumflex", "cedilla", "macron", "macronbelow", "breve", "brevebelow", "ring", "caron", "ogonek", "dotaccent", "hungarumlaut", "commaturnedabove"],
            "se_euro": ["acute", "grave", "dieresis", "circumflex", "cedilla", "breve", "caron", "commaaccent"],
            "vietnam": ["acute", "grave", "circumflex", "tilde", "hookabove", "horn", "breve", "dotbelow"],
            "gf_core": ["acute", "circumflex", "dieresis", "grave", "ring", "tilde", "cedilla"],
            "gf_plus": ["acute", "circumflex", "dieresis", "grave", "ring", "tilde", "cedilla", "breve", "caron", "dotaccent", "dotbelow", "hookabove", "horn", "hungarumlaut", "macron", "ogonek", "commaaccent", "dblgrave", "invertedbreve", "breve_acute", "breve_grave", "breve_hookabove", "breve_tilde", "circumflex_acute", "circumflex_grave", "circumflex_hookabove", "circumflex_tilde"],
            "gf_pro": ["acute", "circumflex", "dieresis", "grave", "ring", "tilde", "cedilla", "breve", "brevebelow", "caron", "dotaccent", "dotbelow", "hookabove", "horn", "hungarumlaut", "macron", "macronbelow", "ogonek", "commaaccent", "dblgrave", "invertedbreve", "breve_acute", "breve_grave", "breve_hookabove", "breve_tilde", "circumflex_acute", "circumflex_grave", "circumflex_hookabove", "circumflex_tilde"],
            "gf_pro_unique": ["acute", "grave", "dieresis", "breve", "dotaccent"],
            "glyph_list_2": list(self.diacritics_map.keys()) + list(self.double_keys.keys()),
            "koeberlin_s": ["acute", "grave", "dieresis", "circumflex", "tilde", "cedilla"],
            "koeberlin_m": ["acute", "grave", "dieresis", "circumflex", "tilde", "cedilla", "macron", "macronbelow", "breve", "brevebelow", "ring", "caron", "ogonek", "dotaccent", "hungarumlaut", "commaturnedabove", "dotbelow", "hookabove", "horn"],
            "koeberlin_l": ["acute", "grave", "dieresis", "circumflex", "tilde", "hookabove", "horn", "cedilla", "macron", "macronbelow", "breve", "brevebelow", "ring", "caron", "dotbelow", "ogonek", "dotaccent", "commaaccent", "commaturnedabove", "hungarumlaut", "dblgrave", "invertedbreve", "breve_acute", "breve_grave", "breve_hookabove", "breve_tilde", "circumflex_acute", "circumflex_grave", "circumflex_hookabove", "circumflex_tilde"],
            "koeberlin_xl": ["acute", "grave", "dieresis", "circumflex", "tilde", "hookabove", "horn", "cedilla", "macron", "macronbelow", "breve", "brevebelow", "ring", "caron", "dotbelow", "ogonek", "dotaccent", "commaaccent", "commaturnedabove", "hungarumlaut", "dblgrave", "invertedbreve", "breve_acute", "breve_grave", "breve_hookabove", "breve_tilde", "circumflex_acute", "circumflex_grave", "circumflex_hookabove", "circumflex_tilde"],
            "underware": ["acute", "grave", "dieresis", "circumflex", "tilde", "cedilla", "macron", "breve", "ring", "caron", "ogonek", "dotaccent", "commaaccent", "hungarumlaut"],
            "todos": list(self.diacritics_map.keys()) + list(self.double_keys.keys())
        }
        
        diacritics_to_activate = set()
        
        for key, checkbox in standards_map.items():
            if checkbox.get():
                diacritics_to_activate.update(region_definitions[key])
                    
        if g2.region_portuguese.get(): diacritics_to_activate.update(region_definitions["portugues"])
        if g2.region_western.get(): diacritics_to_activate.update(region_definitions["western"])
        if g2.region_central.get(): diacritics_to_activate.update(region_definitions["central"])
        if g2.region_se_euro.get(): diacritics_to_activate.update(region_definitions["se_euro"])
        if g2.region_vietnam.get(): diacritics_to_activate.update(region_definitions["vietnam"])
        if g2.region_all.get(): diacritics_to_activate.update(region_definitions["todos"])
        
        if not diacritics_to_activate:
            return
        
        for diacritic, checkbox in self.diacritics_map.items():
            checkbox.set(diacritic in diacritics_to_activate)

    def check_combining(self, font, combining_name):
        if combining_name in self.combining_cache:
            return self.combining_cache[combining_name]
        exists = combining_name in font.glyphs
        self.combining_cache[combining_name] = exists
        return exists

    def ensure_combining_mark(self, font, comb_name):
        if comb_name in font.glyphs:
            self.combining_cache[comb_name] = True
            return False
        try:
            new_accent = GSGlyph(comb_name)
            font.glyphs.append(new_accent)
            new_accent.updateGlyphInfo()
            self.combining_cache[comb_name] = True
            return True
        except Exception as err:
            # Case when glyph already exists with altered case or native mapping
            print(f"⚠️ Warning when creating combining mark {comb_name}: {err}")
            self.combining_cache[comb_name] = True
            return False

    def is_ligature(self, name):
        if name.endswith(".liga") or name.endswith(".dlig") or "_" in name:
            return True
        base_name = name.split(".")[0]
        return base_name in self.common_ligatures

    def is_already_accented(self, base_name_no_suffix):
        info = Glyphs.glyphInfoForName(base_name_no_suffix)
        if info is not None:
            try:
                components = info.components
                if components and len(components) > 1:
                    return True
            except Exception:
                pass
        return base_name_no_suffix.lower() in self.fallback_composite_bases

    def generate_diacritics(self, sender):
        Glyphs.showMacroWindow()
        Glyphs.clearLog()
        
        font = Glyphs.font
        if not font:
            print("Error: No document open.")
            return
        
        g1 = self.w.group_tab0
        g2 = self.w.group_tab1
        
        self.combining_cache = {}
        target_diacritics = [d for d in self.diacritics_list if self.diacritics_map[d].get()]
        
        if not target_diacritics:
            print("Warning: Select at least one diacritic to generate.")
            return
            
        case_upper = g1.generate_uppercase.get()
        case_lower = g1.generate_lowercase.get()
        case_sc = g1.generate_smallcaps.get()
        
        if not any([case_upper, case_lower, case_sc]):
            print("Warning: Select at least one case type.")
            return
            
        should_regenerate = g1.regenerate_existing.get()
        ignore_ligatures = g1.ignore_ligatures.get()
        ignore_non_exporting = g1.ignore_non_exporting.get()
        generate_comb_missing = g1.generate_comb.get()
        allow_case = g1.generate_comb_case.get()
        allow_narrow = g1.generate_comb_narrow.get()

        font.disableUpdateInterface()
        created_glyphs = []

        try:
            diacritics_no_narrow = set(["ogonek", "cedilla", "dotbelow", "macronbelow", "ring", "horn", "dotaccent", "hungarumlaut", "commaaccent"])

            active_regions = []
            checked_standards = [
                ("gf_core", g2.region_gf_core.get()), ("gf_plus", g2.region_gf_plus.get()),
                ("gf_pro", g2.region_gf_pro.get()), ("gf_pro_unique", g2.region_gf_pro_unique.get()),
                ("glyph_list_2", g2.region_glyph_list_2.get()), ("koeberlin_s", g2.region_koeberlin_s.get()),
                ("koeberlin_m", g2.region_koeberlin_m.get()), ("koeberlin_l", g2.region_koeberlin_l.get()),
                ("koeberlin_xl", g2.region_koeberlin_xl.get()), ("underware", g2.region_underware.get())
            ]
            
            active_standards = [st[0] for st in checked_standards if st[1]]
            
            if active_standards:
                active_regions = active_standards
            else:
                if g2.region_portuguese.get(): active_regions.append("portugues")
                if g2.region_western.get(): active_regions.append("western")
                if g2.region_central.get(): active_regions.append("central")
                if g2.region_se_euro.get(): active_regions.append("se_euro")
                if g2.region_vietnam.get(): active_regions.append("vietnam")
            
            use_all_regions = g2.region_all.get()

            # RIGOROUS LIST SEPARATION
            processing_list = list(target_diacritics)
            double_processing_list = []

            for double_key in self.double_keys.keys():
                key_parts = double_key.split("_")
                if not (key_parts[0] in target_diacritics and key_parts[1] in target_diacritics):
                    continue

                valid_double = False
                if use_all_regions:
                    valid_double = True
                else:
                    for region in active_regions:
                        if region in self.legal_map and double_key in self.legal_map[region]:
                            valid_double = True
                            break
                if valid_double:
                    double_processing_list.append(double_key)

            allow_doubles = bool(double_processing_list)
            general_processing_list = processing_list + double_processing_list

            if g1.scope_choice.get() == 0:
                if not font.selectedLayers:
                    print("Warning: No glyphs selected in Font View.")
                    return
                raw_glyphs = [layer.parent for layer in font.selectedLayers if layer.parent and layer.parent.category == "Letter"]
            else:
                raw_glyphs = [glyph for glyph in font.glyphs if glyph.category == "Letter"]
                
            base_letters = []
            for g in raw_glyphs:
                name = g.name
                if "comb" in name or g.category != "Letter": continue
                if ignore_non_exporting and not g.export: continue
                if ignore_ligatures and self.is_ligature(name): continue
                
                # IF DOUBLES ARE NOT VALID IN THIS SET, BLOCK ANY COMPOSITE BASE
                if not allow_doubles and self.is_already_accented(name.split(".")[0]):
                    continue
                    
                base_letters.append(g)

            total_steps = len(base_letters) * len(general_processing_list)
            current_step = 0
            self.w.progress_bar.set(0)

            # --- DYNAMIC COMBINING MARKS FILTERING ---
            if generate_comb_missing:
                self.w.status_text.set("Generating missing combining marks...")
                combs_to_check = []
                
                # Strictly add single selected diacritics
                for acc in target_diacritics:
                    if acc == "commaturnedabove":
                        combs_to_check.append("commaturnedabovecomb")
                        continue
                    combs_to_check.append(f"{acc}comb")
                    if acc == "caron": 
                        combs_to_check.append("caroncomb.alt")
                    if allow_case and case_upper: 
                        combs_to_check.append(f"{acc}comb.case")

                # Strictly add allowed double pairs per region/standard
                for double_key in double_processing_list:
                    combs_to_check.append(self.double_keys[double_key])

                for comb_name in combs_to_check:
                    # Safety check to avoid collision with existing composite glyphs
                    if comb_name not in font.glyphs:
                        if self.ensure_combining_mark(font, comb_name):
                            print(f"Mark created: {comb_name}")
                            created_glyphs.append(comb_name)

            print("\n–––> STEP 2: Assembling composite accented glyphs <––––")
            
            narrow_characters = set(["i", "j", "l", "t", "f", "r", "i.sc", "j.sc", "l.sc", "t.sc", "I"])
            alt_caron_glyphs = set(["dcaron", "tcaron", "lcaron"])
            
            for base_glyph in base_letters:
                raw_name = base_glyph.name
                if "comb" in raw_name: continue
                if ignore_ligatures and self.is_ligature(raw_name): continue
                if ignore_non_exporting and not base_glyph.export: continue
                
                if "." in raw_name:
                    parts = raw_name.split(".", 1)
                    clean_base = parts[0]
                    suffix = "." + parts[1]
                else:
                    clean_base = raw_name
                    suffix = ""
                
                is_smallcap = (".sc" in raw_name or ".smcp" in raw_name) or (base_glyph.case == 3)
                
                if base_glyph.subCategory == "Uppercase" or base_glyph.case == 1:
                    is_uppercase, is_lowercase = True, False
                elif base_glyph.subCategory == "Lowercase" or base_glyph.case == 2:
                    is_uppercase, is_lowercase = False, True
                elif is_smallcap:
                    is_uppercase, is_lowercase = False, False
                else:
                    is_uppercase = (clean_base.isupper() and len(clean_base) == 1)
                    is_lowercase = not is_uppercase
                
                if is_uppercase and not case_upper: continue
                if is_lowercase and not case_lower: continue
                if is_smallcap and not case_sc: continue
                
                if is_lowercase and clean_base in self.dotless_map:
                    base_for_component = self.dotless_map[clean_base]
                    base_for_name = clean_base
                    lowercase_root = clean_base
                else:
                    base_for_component = raw_name
                    base_for_name = clean_base
                    lowercase_root = clean_base.lower()
                
                needs_narrow = allow_narrow and ((lowercase_root in narrow_characters) or (raw_name in narrow_characters) or (clean_base in narrow_characters))
                
                for target_item in general_processing_list:
                    current_step += 1
                    
                    is_double_target = target_item in self.double_keys

                    if total_steps > 0:
                        progress = (float(current_step) / total_steps) * 100
                        self.w.progress_bar.set(progress)
                        self.w.status_text.set(f"Analyzing: /{raw_name} with {target_item} ({int(progress)}%)")

                    actual_acc = self.double_keys[target_item] if is_double_target else target_item

                    if actual_acc == "commaturnedabove" and is_uppercase:
                        continue

                    # REGION / STANDARD FILTER
                    if not use_all_regions:
                        valid_in_region = False
                        for region in active_regions:
                            if region in self.legal_map and target_item in self.legal_map[region] and lowercase_root in self.legal_map[region][target_item]:
                                valid_in_region = True
                                break
                        if not valid_in_region:
                            continue
                    
                    if is_double_target:
                        comb_parts = actual_acc.split("_")
                        accent_suffix = comb_parts[0].replace("comb", "") + comb_parts[1].replace("comb", "")
                        clean_composite_name = f"{base_for_name}{accent_suffix}"
                    else:
                        clean_composite_name = f"{base_for_name}{target_item}"

                    final_potential_name = f"{clean_composite_name}{suffix}"
                    glyph_info = Glyphs.glyphInfoForName(clean_composite_name)
                    
                    if glyph_info and glyph_info.category == "Letter":
                        glyph_exists = final_potential_name in font.glyphs
                        
                        # EXISTENCE CHECK: If not set to overwrite, skip silently
                        if glyph_exists and not should_regenerate:
                            continue
                            
                        if not glyph_exists:
                            try:
                                new_glyph = GSGlyph(final_potential_name)
                                font.glyphs.append(new_glyph)
                            except Exception as err:
                                print(f"⚠️ Skipped glyph {final_potential_name} (already exists in font): {err}")
                                continue
                        else:
                            new_glyph = font.glyphs[final_potential_name]
                            
                        if suffix:
                            new_glyph.updateGlyphInfo()
                            new_glyph.category = "Letter"
                            if is_smallcap:
                                new_glyph.subCategory = "Lowercase"
                                new_glyph.case = 3
                            else:
                                new_glyph.subCategory = glyph_info.subCategory
                        else:
                            new_glyph.updateGlyphInfo()
                            
                        new_glyph.updateGlyphInfo()
                            
                        for master in font.masters:
                            layer = new_glyph.layers[master.id]
                            if hasattr(layer, "shapes"):
                                del layer.shapes[:]
                            else:
                                layer.clear()
                            
                            layer.anchors = []
                            comp_base = GSComponent(base_for_component)
                            comp_base.alignment = 0
                            
                            if hasattr(layer, "shapes"):
                                layer.shapes.append(comp_base)
                            else:
                                layer.components.append(comp_base)
                            
                            final_accent_name = None
                            
                            if not is_double_target:
                                if target_item == "caron" and not is_smallcap and clean_composite_name in alt_caron_glyphs:
                                    if self.check_combining(font, "caroncomb.alt"):
                                        final_accent_name = "caroncomb.alt"
                                
                                if not final_accent_name:
                                    if is_smallcap:
                                        sc_name = f"{target_item}comb.sc"
                                        if self.check_combining(font, sc_name):
                                            final_accent_name = sc_name
                                        elif self.check_combining(font, f"{target_item}comb"):
                                            final_accent_name = f"{target_item}comb"
                                            
                                    elif is_uppercase:
                                        if needs_narrow and target_item not in diacritics_no_narrow:
                                            narrow_case_name = f"{target_item}comb.narrow.case"
                                            if self.check_combining(font, narrow_case_name):
                                                final_accent_name = narrow_case_name
                                        
                                        if not final_accent_name and allow_case:
                                            standard_case_name = f"{target_item}comb.case"
                                            if self.check_combining(font, standard_case_name):
                                                final_accent_name = standard_case_name
                                    else:
                                        if needs_narrow and target_item not in diacritics_no_narrow:
                                            narrow_standard_name = f"{target_item}comb.narrow"
                                            if self.check_combining(font, narrow_standard_name):
                                                final_accent_name = narrow_standard_name
                                
                                if not final_accent_name:
                                    if target_item == "commaturnedabove":
                                        standard_comb_name = "commaturnedabovecomb"
                                    else:
                                        standard_comb_name = f"{target_item}comb"

                                    if suffix and self.check_combining(font, f"{standard_comb_name}{suffix}"):
                                        final_accent_name = f"{standard_comb_name}{suffix}"
                                    elif self.check_combining(font, standard_comb_name):
                                        final_accent_name = standard_comb_name
                                    elif self.check_combining(font, target_item):
                                        final_accent_name = target_item
                            else:
                                if self.check_combining(font, actual_acc):
                                    final_accent_name = actual_acc
                            
                            if final_accent_name:
                                comp_accent = GSComponent(final_accent_name)
                                comp_accent.alignment = 0
                                if hasattr(layer, "shapes"):
                                    layer.shapes.append(comp_accent)
                                else:
                                    layer.components.append(comp_accent)
                            else:
                                print(f"⚠️ Warning: Combining mark glyph not found for {target_item} in {final_potential_name}")
                                
                            if hasattr(layer, "recomposite"):
                                layer.recomposite()
                            elif hasattr(layer, "alignComponents"):
                                layer.alignComponents()

                            if hasattr(layer, "updateMetrics"):
                                layer.updateMetrics()
                            elif hasattr(layer, "syncMetrics"):
                                layer.syncMetrics()
                            
                        new_glyph.updateGlyphInfo()
                        status_type = "Regenerated" if glyph_exists else "Generated"
                        print(f"{status_type}: {final_potential_name} (Base: {base_for_component}, Accent: {final_accent_name})")
                        created_glyphs.append(final_potential_name)
                            
        except Exception as e:
            print(f"Error during processing: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            font.enableUpdateInterface()
            self.w.progress_bar.set(100)
            self.w.status_text.set(f"Completed! Total glyphs: {len(created_glyphs)}")
            if font.currentTab and hasattr(font.currentTab, "graphicView"):
                font.currentTab.graphicView().setNeedsDisplay_(True)
            
        print("\n========================================")
        print(f"Process completed. Total processed glyphs: {len(created_glyphs)}")
        
        if g1.open_tab.get() and created_glyphs:
            tab_text = "/" + "/".join(created_glyphs)
            font.newTab(tab_text)

# Instantiate to run
generator_app = DiacriticsGeneratorInterface()
