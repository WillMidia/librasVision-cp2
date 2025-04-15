# LibrasVision - Reconhecimento de Língua Brasileira de Sinais

**LibrasVision** é uma aplicação de visão computacional que reconhece gestos manuais da Língua Brasileira de Sinais (Libras) usando a webcam.  
O projeto é uma **prova de conceito (POC)**, com soluções paliativas para algumas letras com movimento, devido às limitações do MediaPipe em detectar profundidade e movimentos mais finos.

🔗 Repositório oficial: [github.com/WillMidia/librasVision-cp2](https://github.com/WillMidia/librasVision-cp2)

---

## ✨ Funcionalidades

- Detecção de gestos em tempo real via webcam  
- Reconhecimento de diversas letras do alfabeto em Libras  
- Modo desafio onde o usuário deve soletrar seu nome com os sinais  
- Feedback visual com letra detectada, progresso e tempo

---

## 🛠️ Requisitos

- Python 3.7+
- OpenCV
- MediaPipe
- NumPy

Instale as dependências com:

```bash
pip install -r requirements.txt
```

---

## ▶️ Como Usar

Execute o script principal:

```bash
python libras_vision.py
```

### Controles

- **ENTER**: Iniciar o desafio
- **Backspace**: Apagar última letra
- **C**: Limpar nome
- **M**: Voltar ao menu após o desafio
- **Q**: Sair do programa

---

## Letras Suportadas

A aplicação reconhece as seguintes letras do alfabeto em Libras:

**A, B, C, D, E, F, G, H, I, K, L, M, N, O, P, R, S, T, U, V, W, X, Y**

> ⚠️ **Disclaimer:** Algumas letras passaram por adaptações para funcionar com mais estabilidade no MediaPipe. Abaixo estão os ajustes feitos nos sinais, levando em conta limitações de detecção:
>
> - **C / O** – Mantêm os sinais tradicionais, mas funcionam melhor com a **mão esquerda**.  
> - **F** – Apenas o **dedo indicador deve estar abaixado**.  
> - **H** – Estique **apenas o indicador e o mindinho**.  
> - **K** – Estique o **indicador, anelar e polegar**.  
> - **M** – Todos os dedos **esticados**.  
> - **N** – **Apenas o mindinho abaixado**.  
> - **T** – **Indicador e polegar abaixados**.  
> - **X** – Estique **anelar e mindinho**.

Essas adaptações garantem um reconhecimento mais estável com os recursos atuais.

---
