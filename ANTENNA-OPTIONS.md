# Opções para prender a antena

A antena do Orange Pi Zero 3 é redonda, preta e comprida, com cabo IPEX. O conector fica na placa principal, perto e acima do cartão microSD.

Em todas as opções, a antena fica do lado de fora do case, deitada. Na opção A ela fica na parede da saída de ar, perto do topo (não no teto). Na opção B ela fica na face das USB da placa USB, mais abaixo.

Medidas de partida, a confirmar com paquímetro: 5 mm de grossura e 60 mm de comprimento. A parede tem cerca de 55 mm, então a ponta pode passar um pouco.

| Opção | Como é | Vantagem | Desvantagem |
|---|---|---|---|
| A. Presilhas em C | 2 ganchos abertos na parede. A antena entra de lado, com um clique. | Tira e põe fácil, sem peças extras | A presilha pode rachar se a antena for mais grossa que o previsto |
| B. Canal + abraçadeiras | Canal raso na parede, com 2 fendas para abraçadeiras finas | Bem firme | Precisa de abraçadeiras; troca exige cortar |
| C. Argolas fechadas | 2 argolas fechadas. A antena entra pela ponta. | Firme, sem peças extras | O cabo e o conector precisam passar pelas argolas |
| D. Canal + fita | Canal raso. A antena é colada com fita dupla face. | Mais simples de imprimir | Difícil de tirar; a fita perde força com calor |

## Escolhas feitas

| Branch | Opção | Onde |
|---|---|---|
| `feature/antena-holder` (tag `v-antenna-holder`) | A | Parede da saída de ar, perto do topo |
| `feature/antenna-zip-tie` | B | Face das USB da placa USB, abaixo delas |

### Opção B (`feature/antenna-zip-tie`)

A antena fica deitada ao longo da face das USB da placa USB, abaixo da janela delas e acima da fenda do microSD. Um bloco na parede tem um canal meio redondo. Atrás do canal há 2 túneis verticais. Cada abraçadeira entra por baixo do túnel, sobe, dá a volta na antena e fecha. O cabo entra por um furo de 3,2 mm logo acima do bloco, entre as USB e o P2.

| Parâmetro (`case.py`) | Valor | O que é |
|---|---|---|
| `ANT_D`, `ANT_L` | 5,0 / 60,0 mm | Grossura e comprimento da antena |
| `ANT_Z` | 10,0 mm | Altura do eixo da antena |
| `CH_R` | 2,7 mm | Raio do canal |
| `TIE_W`, `TIE_T` | 3,5 / 1,4 mm | Túnel para abraçadeira de até 3 mm x 1,2 mm |
| `TIE_OFFSET` | 18 mm | Túneis a 36 mm um do outro |
| `CRADLE_L` | 56 mm | Comprimento do bloco |
| `ANT_HOLE`, `ANT_HOLE_D` | x 10,5, z 15,6 / 3,2 mm | Furo de entrada do cabo |

### Opção A (`feature/antena-holder`)

| Parâmetro (`case.py`) | Valor | O que é |
|---|---|---|
| `ANT_D`, `ANT_L` | 5,0 / 60,0 mm | Grossura e comprimento da antena |
| `ANT_FIT` | 0,2 mm | Aperto: a presilha é 0,2 mm menor que a antena |
| `CLIP_T` | 1,6 mm | Parede da presilha |
| `CLIP_W` | 6,0 mm | Largura de cada presilha |
| `CLIP_OPEN` | 0,75 | Abertura da boca, em fração da grossura (3,75 mm) |
| `ANT_CLIPS_Y` | centro ± 15 mm | Posição das 2 presilhas |
| `ANT_HOLE`, `ANT_HOLE_D` | y 17,25, z 8,0 / 3,2 mm | Furo de saída do cabo |

A boca da presilha fica virada para fora da parede. A tampa imprime com o teto na mesa, então cada presilha imprime como um anel deitado, sem suporte.
