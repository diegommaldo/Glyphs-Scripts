# MenuTitle: Verificar e Abrir Métricas com Decimais
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

thisFont = Font
# Limpa a seleção anterior para focar nos resultados
glifos_com_erro = []

print("Buscando glifos com métricas decimais na Master atual...")
print("-" * 50)

# Itera sobre os glifos da fonte
for glyph in thisFont.glyphs:
    # Foca na camada da Master selecionada no momento
    layer = glyph.layers[thisFont.selectedFontMaster.id]
    
    lsb = layer.LSB
    rsb = layer.RSB
    width = layer.width
    
    # Verifica se os valores possuem decimais (usando mod 1)
    if (lsb % 1 != 0) or (rsb % 1 != 0) or (width % 1 != 0):
        info = f"Glifo: {glyph.name:<20} | LSB: {lsb:<8} | RSB: {rsb:<8} | Width: {width:<8}"
        print(info)
        glifos_com_erro.append(glyph.name)

print("-" * 50)

if glifos_com_erro:
    print(f"Sucesso! {len(glifos_com_erro)} glifos encontrados e abertos para edição.")
    
    # Monta a string para a nova aba (ex: /A/B/C)
    tab_string = "/" + "/".join(glifos_com_erro)
    
    # Abre a nova aba no Glyphs
    thisFont.newTab(tab_string)
else:
    print("Nenhum glifo com métricas decimais encontrado. Tudo limpo!")