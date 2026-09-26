<div  align='center' background-color='#fff'>

   <h1><code>Sticker Notes</code></h1>

   <p>
      <strong>📄 Notas adesivas para sistemas desktop. Simples, leves e sempre à mão.</strong>
   </p>

   <img src='https://img.shields.io/github/languages/top/anabeatrizfrez/sticker-notes' alt='Linguagem mais utilizada' />
   <img src='https://img.shields.io/github/last-commit/anabeatrizfrez/sticker-notes' alt='Último commit' />
   <img src='https://img.shields.io/github/license/anabeatrizfrez/sticker-notes' alt='Licença' />
   
</div>

<br>

## ⬇️ Como instalar

### 🪟 Windows:

- Baixe o `Sticker-Notes-Setup.exe` na aba [Releases](../../releases) e execute. O instalador cuida de tudo: cria atalho no Menu Iniciar e pergunta se você quer que o app abra junto com o Windows.

- Se preferir não instalar nada, o `sticker-notes-portable.exe` também está disponível na mesma página: só baixar e rodar.


### 🐧 Linux:


- Baixe o `.deb` na aba [Releases](../../releases) e instale:

```bash
sudo apt install ./sticker-notes_<versão>_amd64.deb
```

<p align='center'>ou</p>

- Instalar via terminal (requer Python 3.9+):

```bash
# Se não tiver python 3.9+ instalado:

   $ sudo apt update
   $ sudo apt install python3
   $ sudo apt install python3-pip

# Instalação:

   $ pipx install git+https://github.com/anabeatrizfrez/sticker-notes.git # Instalar
   $ sticker-notes # Executar
```

<br>

## 🔨 Como usar

Quando o app estiver aberto, o ícone fica na bandeja do sistema (perto do relógio).

- **Criar uma nota**: clique no ícone da bandeja → Nova nota
- **Escrever**: clique na nota para focar e começar a digitar
- **Mover**: com a nota desfocada, clique e arraste. Com ela focada, arraste pela barra no topo
- **Redimensionar**: arraste o triângulo no canto inferior direito
- **Mudar a cor**: clique no ícone de gota (aparece quando a nota está focada)
- **Marcar uma tarefa**: use `Ctrl+T` para criar uma linha de tarefa, e clique no checkbox para marcar como feita
- **Fixar uma nota**: `Ctrl+P` mantém ela por cima de todas as outras janelas

<br>

### Atalhos


| Tecla | O que faz |
|---|---|
| `Ctrl+N` | Nova nota |
| `Ctrl+D` | Duplicar nota |
| `Ctrl+W` | Excluir nota |
| `Ctrl+T` | Nova tarefa |
| `Ctrl+P` | Fixar/desafixar |
| `Ctrl+B` / `Ctrl+I` / `Ctrl+U` | Negrito / Itálico / Sublinhado |
| `Ctrl+Shift+X` | Riscado |
| `Ctrl+Shift+C` | Trocar cor |

<br>

## 🔄 Como atualizar

<details>
   <summary>
      <span style="font-size: 1.3em; font-weight: bold;">🪟 Windows</span>
   </summary>
   <br>

   - Baixe o novo `Sticker-Notes-Setup.exe` na aba [Releases](../../releases) e execute por cima da versão atual. O instalador atualiza sem perder suas notas.
</details>

<br>

<details>
   <summary>
      <span style="font-size: 1.3em; font-weight: bold;">🐧 Linux</span>
   </summary>
   <br>

   ### Linux (.deb):

   ```bash
      $ sudo apt install ./sticker-notes_<nova versão>_amd64.deb
   ```

   ### Terminal (pipx):

   ```bash
      $ pipx upgrade sticker-notes
   ```
</details>

<br>

> Quando houver uma versão nova disponível, o próprio app avisa com um balão na bandeja do sistema.

<br>

## 💔 Como desinstalar

<details>
   <summary>
      <span style="font-size: 1.3em; font-weight: bold;">🪟 Windows</span>
   </summary>
   <br>

   ### Windows (instalador):

   - Configurações → Aplicativos → Sticker Notes → Desinstalar.

   ### Windows (portátil):

   - Apague o `sticker-notes-portable.exe`. Se tiver ativado o início com o Windows, desative antes pelo menu da bandeja.

</details>

<br>

<details>
   <summary>
      <span style="font-size: 1.3em; font-weight: bold;">🐧 Linux</span>
   </summary>
   <br>

   
   ### Linux (.deb):

   ```bash
      $ sudo apt remove sticker-notes
   ```

   ### Terminal (pipx):

   ```bash
      $ pipx uninstall sticker-notes
   ```

</details>

<br>

## 💾 Onde ficam as notas salvas

As notas ficam na pasta do seu usuário:

| Sistema | Local |
|---|---|
| Windows | `%APPDATA%\StickerNotes\notas.json` |
| Linux | `~/.local/share/sticker-notes/notas.json` |

<br>

## 📝 Licença

Este projeto está sob licença do MIT - Veja a [LICENSE](LICENSE) para mais informações.