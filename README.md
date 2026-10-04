# RE5-TRAINER-TU5

O trainer +8 da TeamXPG (t3fury) para o Resident Evil 5 de Xbox 360,
com 3 correções. Os endereços foram conferidos com o executável da TU5 e
com outras duas versões de trainer. Testado num Xbox 360 desbloqueado.

> Não é oficial. O trainer e o loader originais são da TeamXPG e foram
> publicados no XPGamesaves. Este repositório distribui a versão
> corrigida e documenta tudo o que mudou.

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `trainer/Trainer.xex` | O trainer, corrigido |
| `trainer/Resident Evil 5 Trainer_Loader.xex` | O loader original, sem mudança |
| `trainer/LEIA-ME.txt` | Instruções curtas, para levar junto para o console |
| `ferramentas/conferir-re5.py` | Confere se uma ISO, um `default.xex` ou um arquivo de TU serve para o trainer |

## Requisitos

- **Xbox 360 desbloqueado** com o **Xbdm** carregado, por exemplo como
  plugin do DashLaunch. O trainer grava no jogo pelo Xbdm; sem ele, grava
  direto na memória, o que não foi testado.
- **Resident Evil 5 na TU5** (versão `0.0.5.3`), do disco World
  (Media ID `5B2A79D5`). O disco vem na versão `0.0.0.3`, então é
  preciso instalar a TU5. Veja [Conferir o jogo](#conferir-o-jogo).

## Como usar

1. Copie os dois `.xex` da pasta `trainer/` para a mesma pasta no console.
2. Abra o `Resident Evil 5 Trainer_Loader.xex` (pelo Aurora, FSD etc.).
3. Tem que aparecer a notificação **"Resident Evil 5 TU5 +8 Trainer Loaded"**.
4. Abra o Resident Evil 5 sem reiniciar o console.
5. Já dentro do jogo, com o **controle 1**, segure o **D-pad para cima** e
   aperte **START** (os dois juntos, por 1 segundo). Abre uma caixa
   pedindo uma senha de 4 botões.
6. Digite a combinação **nessa caixa**. Se ela não fechar sozinha, aperte A.

Apertar os 4 botões sem abrir a caixa não faz nada. Esse passo não estava
na postagem original e é o motivo mais comum de "o trainer não funciona".

| Trapaça | Combinação |
|---|---|
| Vida infinita | RT RT RT RT |
| Munição infinita | LT LT LT LT |
| Granadas infinitas | RB RB RB RB |
| Minas infinitas | X X X X |
| Dinheiro infinito | LB LB LB LB |
| Pontos do Mercenaries | Y Y Y Y |
| Pontos das DLCs (Lost in Nightmares e Desperate Escape) | LB RB LB RB |
| Parar o relógio | LT RT LT RT |
| Todas as trapaças | D-pad cima ×4 |
| Ver a lista de códigos | D-pad baixo ×4 |

Depois de cada código aparece "... Activated" (ou "Deactivated") e o
controle vibra. A mesma combinação liga e desliga. Para outro código,
abra a caixa de novo.

## O que foi corrigido

| Endereço no trainer | Antes | Depois | Motivo |
|---|---|---|---|
| `0x9122CB5C` | `93BA0414` | `93DF2BCC` | Pontos das DLCs: ao desligar, gravava uma instrução errada em `0x826919E4` |
| `0x9122CB60` | `93BA0414` | `917F2BCC` | Pontos das DLCs: ao desligar, gravava uma instrução errada em `0x8230B264` |
| `0x9122CB58` | `93BA0414` | `938A0414` | Mercenaries: ao desligar, gravava uma instrução errada em `0x822394A8` |
| `0x9122B5C0` | `611B3F14` | `60FB125C` | Mercenaries e "todas": `ori r27,r8,0x3F14` → `ori r27,r7,0x125C` (o destino `0x07473F14` vira `0x8224125C`) |
| `0x9122CB50` | `0FFFFFFF` | `90680414` | O valor que ia para `0x07473F14` vira a instrução original de `0x8224125C` |

1. **Pontos das DLCs e do Mercenaries, ao desligar.** O original gravava
   `93BA0414` no lugar da instrução de cada endereço, o que podia travar ou
   bagunçar o jogo. Agora, ao desligar qualquer trapaça, o jogo volta
   exatamente ao original: as 13 instruções restauradas batem com o
   executável da TU5.
2. **Pontos do Mercenaries no endereço fixo.** Além de travar os pontos, o
   original gravava um número grande direto na variável dos pontos, em
   `0x07473F14`. Esse é o endereço que a variável tinha no console do
   autor; a memória de dados pode mudar de lugar em outra versão ou
   montagem do jogo. Essa gravação foi trocada por uma inofensiva: os
   pontos ficam travados no valor atual, em vez de irem para o máximo.

O XEX foi remontado com os hashes das páginas, o hash da imagem e o hash
do cabeçalho recalculados, e cifrado com a mesma chave de sessão do
original. A compressão passou de LZX para a básica. A assinatura RSA não é
conferida em console desbloqueado.

## Conferido com outras versões

- **XPG Chameleon v1.30** (versão mais nova do mesmo autor, 2014): mesmos
  endereços, e as correções 1 e 2 dos pontos das DLCs e do Mercenaries
  feitas do mesmo jeito (`93DF2BCC`, `917F2BCC` e `938A0414`). O Chameleon
  tem um erro que esta versão não tem: ao desligar o dinheiro infinito,
  grava `916300D4` em `0x828007B0`, onde o original é `816300D4`.
- **RE5 \*RF\* TU5 +6** (outro trainer): mesmos endereços para vida,
  munição, granadas e minas.

## Conferir o jogo

O script lê o Title ID, o Media ID e a versão direto da ISO (XISO ou
disco completo do Redump), de um `default.xex` ou de um arquivo de TU
(pacote STFS). Ele só lê, não grava nada, e não precisa de bibliotecas.

```
python3 ferramentas/conferir-re5.py "Resident Evil 5 (World).iso"
```

Com a ISO World do Redump, a saída é:

```
Tipo:       ISO
Title ID:   434307D4 (Resident Evil 5)
Media ID:   5B2A79D5 (o mesmo do trainer)
Versão:     0.0.0.3 (base 0.0.0.3)

Resultado: mesmo disco do trainer, mas sem a TU5 (a TU5 mostra 0.0.5.3).
           Instale e ative a TU5 antes de usar o trainer.
```

## Cuidados

- Só use os códigos com o RE5 aberto e na TU5. O trainer não confere o
  jogo nem a versão: em outro jogo ou versão ele grava nos mesmos
  endereços e pode travar.
- A vida infinita não segura em alguns ataques com cena.
- Desligar o console tira o trainer da memória: abra o loader de novo.
- Faça backup do save. Use jogando sozinho ou offline.

## SHA-256

| Arquivo | SHA-256 |
|---|---|
| `Trainer.xex` (corrigido) | `51183e1cd4b10573260f3f4be2c1cc6406a708198d63b7b10d273ea3f04db253` |
| `Resident Evil 5 Trainer_Loader.xex` | `eba466ee8a56d72332e14e39e2cc3d8da259db74a349e32f9a99d263c11d4b1d` |
| `Trainer.xex` original, para comparar | `5eb58bd4e7dc5c8d0f2819296291980b323de5c52536c2aba3116ce229408f28` |

## Créditos

- **Trainer e loader:** TeamXPG / t3fury (XPGamesaves). Os direitos são dos
  autores originais; este repositório só distribui a correção, sem fins
  comerciais.
- **Correção, conferência e `conferir-re5.py`:** lux-insider. O script e a
  documentação estão sob a licença MIT ([LICENSE](LICENSE)).
- Resident Evil 5 é marca da Capcom. Este repositório não tem nenhum
  arquivo do jogo.
