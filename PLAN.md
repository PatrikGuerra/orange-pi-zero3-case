# Plano: case para Orange Pi Zero 3 (2 GB) + placa de expansão USB

Case impresso em PETG, com ventoinha integrada e suporte para a antena Wi-Fi.

## 1. Referências achadas

| Projeto | O que tem | Licença | Uso para nós |
|---|---|---|---|
| [MotorBottle/OrangePi-Zero3-3D-Print-Case](https://github.com/MotorBottle/OrangePi-Zero3-3D-Print-Case) | Placa + expansão + ventoinha 2507, arquivo **STEP** | MIT | Base principal: medidas e posição dos furos |
| [ckuzma/opi-zero-3-case](https://github.com/ckuzma/opi-zero-3-case) | Case ventilado com suporte de antena | ver repo | Ideia do suporte de antena; furos M3 de 2,9 mm (rosca) e 3,8 mm (passante) |
| [Printables 997044](https://www.printables.com/model/997044-orange-pi-zero-3-case-30mm-fan) | Ventoinha 30 mm, só a placa | ver página | Altura para dissipador + ventoinha |
| [Printables 572566](https://www.printables.com/model/572566-orange-pi-zero-3-case-with-expansion-board/files) | Case com expansão | ver página | Recortes de USB e P2 da expansão |
| [MakerWorld 1487393](https://makerworld.com/en/models/1487393-orange-pi-zero-3-case-expansion-board) | Expansão, antena movida para cima | ver página | Antena longe da base melhora o sinal |

Lição dos makes: suporte de antena fino impresso em pé sem suporte fica frágil.

## 2. Medidas (conferir com paquímetro)

| Item | Valor de partida | Fonte |
|---|---|---|
| PCB principal | 50 x 55 mm | ficha técnica |
| Furos de fixação | 4, para M3 (ou M2.5) | ckuzma / STEP |
| Placa de expansão | liga no header de 13 pinos, fica ao lado/abaixo | STEP MotorBottle |
| Portas da expansão | 2x USB-A, P2 de áudio, receptor IR | placa |
| Portas da principal | USB-C (força), micro-HDMI, RJ45, USB-A, microSD | placa |
| Ventoinha | 25x25x7 mm (2507), 5 V | MotorBottle |
| Antena | antena flexível com cabo IPEX | kit |

As medidas finais vêm do STEP da MotorBottle, cruzadas com 5 medidas suas (seção 4).

## 3. Design proposto (decidido em 2026-11-24)

Escolhas do usuário: ventoinha 4010 de lado, placa USB montada, sem acesso ao GPIO, dissipadores já colados no chip, antena do lado de fora, case de mesa.

- **Peças**: base + tampa (2 peças), fechadas com 4 parafusos M3 longos.
- **Placa**: em pinos de 4 mm na base; placa USB no lugar dela (posição lida do STEP).
- **Ventoinha 4010 (40x40x10 mm)**: numa parede lateral, soprando para dentro, alinhada com os dissipadores. Furos de 32 mm entre centros, parafusos M3. Grade na frente para proteger os dedos.
- **Fluxo de ar**: entra pela ventoinha, passa no chip, sai por frestas na parede oposta. Sem outras aberturas grandes, para o ar não fugir.
- **Altura**: a ventoinha tem 40 mm; o case fica com cerca de 44 mm por dentro, ou a ventoinha desce abaixo da placa se sobrar espaço.
- **Força da ventoinha**: ventoinha **5 V**, ligada nos pinos 5 V e GND do header (por dentro do case).
- **Antena por fora**: a antena flexível original fica num berço raso por fora, na tampa. Fenda de 3 mm para o cabo IPEX passar.
- **Mesa**: 4 rebaixos de 8 mm na base para pés de borracha.
- **Recortes**: USB-C, micro-HDMI, RJ45, USB-A, as 2 USB e o P2 da placa USB, microSD, LED.
- **Sem GPIO**: tampa fechada em cima dos pinos.
- **Furos**: rosca direto no PETG (2,9 mm) ou insertos de calor M3.

O STEP da MotorBottle está em `reference/motorbottle-case.stp`. Ele traz a placa (forma da Zero2, igual à Zero 3), a placa USB, as USB, o P2, o IR e o header.

### Como ficou o modelo (v1, `case.py`)

- Medida externa: 78,6 x 56,9 x 46,1 mm (branch `feature/fan-inside`: ventoinha dentro).
- Janelas de portas vizinhas com tira de parede menor que 1,5 mm viram uma só.
- **Tampa**: caixa de 5 lados. Imprimir com o teto na mesa.
- **Base**: placa de 3,5 mm que encaixa por dentro da tampa. Imprimir deitada.
- Ventoinha 4010 dentro, encostada na parede -X (lado do GPIO), presa por fora com 4 x M3 x 10 que roscam nos furos da ventoinha. Grade em colmeia na parede.
- Saída de ar: frestas na parede +X, na altura entre a placa e a placa USB.
- Antena: trilhos por fora da parede +X, acima das frestas, com fenda para o cabo.
- Fixação da base: 2 ganchos no lado -X entram em fendas da parede; 2 parafusos M3 x 10 no lado +X. Placa: 4 M3 x 6 nos pinos da base.
- 2 colunas no teto prendem a placa USB com 2 parafusos M3 x 5, por baixo da placa USB, direto na coluna. O teto fica fechado.

### Montagem

1. Parafuse a placa na base (4 x M3 x 6).
2. Vire a tampa de cabeça para baixo. Coloque a placa USB inclinada, com as portas entrando nas janelas (a parede de PETG cede um pouco). Encoste nas 2 colunas e prenda com 2 x M3 x 5.
3. Parafuse a ventoinha por fora da parede -X (4 x M3 x 10). Ligue o cabo dela nos pinos 5 V e GND da placa.
4. Vire a base com a placa e encaixe os 2 ganchos nas fendas da parede -X.
5. Gire a base para fechar. O conector da placa USB encaixa no header de 13 pinos.
6. Prenda a base com 2 x M3 x 10 no lado +X.
- Dissipador: o limite é o vão entre as placas, cerca de 10 mm. O case não muda isso.
- Saídas: `out/lid.stl`, `out/base.stl`, `out/case.step`.
- Checagem: `tools/fit_check.py` cruza o case com o STEP e falha se alguma peça encostar.

## 4. Regras para PETG

| Regra | Valor |
|---|---|
| Parede | 2,0 mm (5 linhas com bico 0,4) |
| Folga peça/encaixe | 0,25 mm por lado |
| Folga portas | 0,5 mm por lado |
| Furo M3 rosca / passante | 2,9 mm / 3,4 mm |
| Furos verticais | impressos de pé, sem suporte |
| Pontes (frestas) | até 10 mm, frestas de 2 mm |
| Sem encaixes de pressão finos | PETG cede e cria fios |
| Orientação | base e tampa com a face plana na mesa |

## 5. Passos

1. Baixar o STEP da MotorBottle e ler posições dos furos e portas.
2. Você mede com paquímetro: distância entre furos (X e Y), altura do conector mais alto, altura da expansão montada, tamanho da antena, tamanho da ventoinha que você tem.
3. Modelo paramétrico em **build123d** (Python), gera STL e STEP. Todas as medidas num só arquivo de parâmetros.
4. Checagem: modelo da placa dentro do case, sem colisão.
5. Imprimir um **teste rápido**: só a base, 1 mm de piso, para conferir furos e portas.
6. Ajustar e imprimir o case completo.

## 6. Perguntas abertas

- Altura dos dissipadores colados (mm)?
- A ventoinha 4010 é de 5 V ou 12 V?
- Qual lado recebe a ventoinha? (padrão: o lado sem portas)
