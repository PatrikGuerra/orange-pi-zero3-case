# Impressão em PETG

Revisão de impressão da versão `v-final-zip-tie`, com as melhorias da branch `feature/print-review`.

## Orientação

| Peça | Arquivo | Na mesa | Suporte |
|---|---|---|---|
| Tampa | `out/lid.stl` | Teto | Não precisa |
| Base | `out/base.stl` | Fundo plano | Não precisa |

Com a tampa de teto na mesa, as torres, as nervuras e as colunas da placa USB crescem do teto para cima. Nada fica solto no ar.

## Configuração sugerida

| Item | Valor |
|---|---|
| Bico | 0,4 mm |
| Camada | 0,2 mm |
| Paredes | 4 linhas (a parede de 2 mm fica toda sólida) |
| Preenchimento | 30 %, giroide |
| Bico / mesa | 235 a 245 °C / 75 a 85 °C |
| Ventoinha da peça | 30 a 50 %; 100 % nas pontes |
| Velocidade de ponte | Baixa (cerca de 20 mm/s) |

## Pontes (aberturas que imprimem sobre o ar)

Com a tampa de cabeça para baixo, a borda de baixo de cada janela vira a borda de cima na impressão. Essa borda imprime como ponte.

| Janela | Ponte |
|---|---|
| USB-A + rede | 25,0 mm |
| USB dupla da placa USB | 17,1 mm |
| USB-C | 5,2 mm |
| micro-HDMI | 8,5 mm |
| Frestas de ar | 2,5 mm |
| Furos das fitas | 3,4 mm |

A ponte de 25 mm é a mais longa. No PETG ela pode cair um pouco, cerca de 0,3 mm. A janela tem 1 mm de folga, então isso não trava o conector. Se cair mais, limpe a borda com estilete.

## Melhorias feitas nesta revisão

| Ponto | Antes | Agora |
|---|---|---|
| Parede entre o furo do cabo e a fenda do microSD | 0,6 mm | 1,1 mm (`MICROSD_CLEAR_Z` 1,5 → 1,0) |
| Borda do teto na mesa | Reta | Chanfro de 0,5 mm (`BED_CHAMFER`) contra o "pé de elefante" |
| Borda de baixo da base | Reta | Chanfro de 0,5 mm, para a base entrar na tampa |
| Fenda do microSD | Aberta até a borda de baixo | Janela fechada na própria parede, 14,5 x 3 mm. O cartão entra depois da montagem. |

A checagem (`tools/fit_check.py`) agora também falha se:

- a parede entre o furo do cabo e a fenda do microSD ficar abaixo de 1 mm;
- sobrar menos de 1 mm de plástico em volta da rosca de uma torre;
- sobrar menos de 1,5 mm em volta da rosca das colunas da placa USB;
- a tampa ou a base perder o chanfro da mesa.

## Pontos de atenção

| Ponto | Medida | O que fazer |
|---|---|---|
| Torre do canto da placa USB | 5 mm, 1,05 mm em volta da rosca | Não dá para crescer: bate na placa USB. Aperte devagar. |
| Rosca M3 direto no PETG | Furo de 2,9 mm | Passe o parafuso uma vez antes de montar. Não aperte demais. |
| Folga placa / parede | 0,3 mm | Se a placa não entrar, aumente `PCB_WALL_GAP`. |
| Folga base / tampa | 0,25 mm | Se ficar justo, aumente `FIT` para 0,3. |
| Furo do cabo da antena | 3 mm | O conector IPEX passa, mas com pouca folga. |
| Cabeças dos parafusos da base | Ficam para fora | Use pés de borracha de 2 mm ou mais. |

## Teste antes da peça toda

Imprima só os 10 mm de baixo da tampa (corte no fatiador). Teste a placa nas janelas das portas e na fenda do microSD.
