#!/usr/bin/env python3
"""Confere se uma ISO (ou um arquivo de TU) do Resident Evil 5 serve para o
trainer TU5. Só lê: não grava nada.

Uso:
    python3 conferir-re5.py "Resident Evil 5 (World).iso"
    python3 conferir-re5.py TU_xxxxxxxx           (arquivo da Title Update)
    python3 conferir-re5.py default.xex
"""
import struct
import sys

TITLE_ID = 0x434307D4
MEDIA_ID = 0x5B2A79D5           # o disco para o qual o trainer foi feito
VERSAO_TU5 = 0x00000503         # versão do default.xex com a TU5 (o disco vem com 0.0.0.3)
PARTICOES = [0, 0x18300000, 0xFD90000, 0x2080000]   # XISO, XGD1, XGD2, XGD3
MAGIC = b"MICROSOFT*XBOX*MEDIA"


def be32(d, o):
    return struct.unpack(">I", d[o:o + 4])[0]


def le16(d, o):
    return struct.unpack("<H", d[o:o + 2])[0]


def le32(d, o):
    return struct.unpack("<I", d[o:o + 4])[0]


def info_xex(cab):
    """(title ID, media ID, versão, versão base) do cabeçalho de um XEX/XEXP."""
    if cab[:4] != b"XEX2":
        return None
    for i in range(be32(cab, 20)):
        chave, valor = be32(cab, 24 + 8 * i), be32(cab, 28 + 8 * i)
        if chave == 0x40006:
            return be32(cab, valor + 12), be32(cab, valor), be32(cab, valor + 4), be32(cab, valor + 8)
    return None


# ---------- ISO (XDVDFS) ----------

def achar_particao(f):
    for p in PARTICOES:
        f.seek(p + 0x10000)
        if f.read(20) == MAGIC:
            return p
    return None


def achar_na_raiz(f, part, nome):
    f.seek(part + 0x10000 + 20)
    setor, tam = struct.unpack("<II", f.read(8))
    f.seek(part + setor * 2048)
    d = f.read(tam)
    o = 0
    while o + 14 <= len(d):
        if le16(d, o) == 0xFFFF:                  # resto do setor vazio
            o = (o // 2048 + 1) * 2048
            continue
        ini, tamarq, n = le32(d, o + 4), le32(d, o + 8), d[o + 13]
        if d[o + 14:o + 14 + n].decode("latin1").lower() == nome:
            return part + ini * 2048, tamarq
        o += (14 + n + 3) & ~3
    return None


def ler_iso(caminho):
    with open(caminho, "rb") as f:
        part = achar_particao(f)
        if part is None:
            return None, "não achei o sistema de arquivos do Xbox nesta ISO"
        achou = achar_na_raiz(f, part, "default.xex")
        if not achou:
            return None, "não achei o default.xex na raiz da ISO"
        pos, _ = achou
        f.seek(pos)
        cab = f.read(12)
        f.seek(pos)
        return f.read(be32(cab, 8)), None


# ---------- TU (pacote STFS: LIVE/CON/PIRS) ----------

def ler_stfs(caminho):
    with open(caminho, "rb") as f:
        d = f.read()
    tam_cab = be32(d, 0x340)
    base = (tam_cab + 0xFFF) & ~0xFFF
    sexo = (~d[0x37B]) & 1
    passo0 = 0xAB if sexo == 0 else 0xAC
    total = be32(d, 0x395)
    topo = 0 if total <= 0xAA else 1

    def dado(b):
        r = (((b + 0xAA) // 0xAA) << sexo) + b
        if b < 0xAA:
            return r
        if b < 0x70E4:
            return r + (((b + 0x70E4) // 0x70E4) << sexo)
        return (1 << sexo) + r + (((b + 0x70E4) // 0x70E4) << sexo)

    def end(b):
        return (dado(b) << 12) + base

    def proximo(b):
        if b < 0xAA:
            n = 0
        else:
            n = (b // 0xAA) * passo0 + (((b // 0x70E4) + 1) << sexo)
            if b // 0x70E4:
                n += 1 << sexo
        a = (n << 12) + base + (b % 0xAA) * 0x18
        if topo == 0:
            a += (d[0x37B] & 2) << 0xB
        elif sexo == 1:
            t1 = (passo0 << 12) + base + ((d[0x37B] & 2) << 0xB)
            a += (d[t1 + (b // 0xAA) * 0x18 + 0x14] & 0x40) << 6
        return d[a + 0x15] << 16 | d[a + 0x16] << 8 | d[a + 0x17]

    def ler(ini, n, tam, seguidos):
        b, partes = ini, []
        for _ in range(n):
            partes.append(d[end(b):end(b) + 0x1000])
            b = b + 1 if seguidos else proximo(b)
        return b"".join(partes)[:tam]

    ft_n = struct.unpack("<H", d[0x37C:0x37E])[0]
    ft_ini = d[0x37E] | d[0x37F] << 8 | d[0x380] << 16
    tabela = ler(ft_ini, ft_n, ft_n * 0x1000, False)
    for o in range(0, len(tabela), 0x40):
        e = tabela[o:o + 0x40]
        if not e[0]:
            continue
        fl = e[0x28]
        nome = e[:fl & 0x3F].decode("latin1").lower()
        if nome.endswith((".xexp", ".xex")) and not fl & 0x80:
            n = e[0x29] | e[0x2A] << 8 | e[0x2B] << 16
            ini = e[0x2F] | e[0x30] << 8 | e[0x31] << 16
            return ler(ini, n, be32(e, 0x34), bool(fl & 0x40)), None
    return None, "não achei nenhum .xex ou .xexp dentro do pacote"


def versao(v):
    return "%d.%d.%d.%d" % (v >> 28, (v >> 24) & 0xF, (v >> 8) & 0xFFFF, v & 0xFF)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    caminho = sys.argv[1]
    with open(caminho, "rb") as f:
        inicio = f.read(4)
    if inicio == b"XEX2":
        with open(caminho, "rb") as f:
            cab, erro = f.read(0x10000), None
        tipo = "executável"
    elif inicio in (b"LIVE", b"CON ", b"PIRS"):
        cab, erro = ler_stfs(caminho)
        tipo = "Title Update"
    else:
        cab, erro = ler_iso(caminho)
        tipo = "ISO"
    if erro:
        print("ERRO:", erro)
        return 1
    info = info_xex(cab)
    if not info:
        print("ERRO: não consegui ler as informações do executável")
        return 1
    tid, mid, ver, vbase = info
    print("Tipo:       %s" % tipo)
    print("Title ID:   %08X %s" % (tid, "(Resident Evil 5)" if tid == TITLE_ID else "(NÃO é o Resident Evil 5)"))
    print("Media ID:   %08X %s" % (mid, "(o mesmo do trainer)" if mid == MEDIA_ID else "(DIFERENTE do trainer: %08X)" % MEDIA_ID))
    print("Versão:     %s (base %s)" % (versao(ver), versao(vbase)))
    print()
    if tid != TITLE_ID:
        print("Resultado: não é o Resident Evil 5.")
    elif mid != MEDIA_ID:
        print("Resultado: é outro disco do RE5. O trainer foi feito para o Media ID %08X;" % MEDIA_ID)
        print("           com este disco não dá para garantir os endereços.")
    elif ver == VERSAO_TU5:
        print("Resultado: mesmo disco do trainer, já na TU5. O trainer serve.")
    elif tipo == "Title Update":
        print("Resultado: é uma atualização do mesmo disco, mas a versão é diferente da TU5")
        print("           (a TU5 mostra %s). Com ela o trainer não serve." % versao(VERSAO_TU5))
    else:
        print("Resultado: mesmo disco do trainer, mas sem a TU5 (a TU5 mostra %s)." % versao(VERSAO_TU5))
        print("           Instale e ative a TU5 antes de usar o trainer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
