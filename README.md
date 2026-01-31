# openFABA

**openFABA** is a command-line tool for inspecting, extracting, and exporting audio 
files for the **FABA** storytelling box. It allows you to convert standard MP3 files 
into FABA-compatible files for specific figures.

This project builds upon the reverse-engineering work by
[wansors](https://github.com/wansors/myfaba-hacks/blob/main/python/redele.py).
At the moment, openFABA supports **only the original FABA device**.

### Disclaimer

openFABA is an independent project and is **not affiliated with or endorsed by FABA**.

This software is provided *as is*, without warranties of any kind. You are responsible 
for how you use it and for any consequences that may arise, including device malfunction 
or account-related actions. Some features may conflict with FABA’s terms of service or 
usage policies.

The goal of openFABA is to:

* simplify the creation of custom, FABA-compatible figures
* enable personalization of figures you already own

We do **not** endorse music piracy, copyright infringement, or any misuse that could 
negatively impact FABA or its ecosystem. FABA is a great company, and we encourage 
supporting them by purchasing their products.

Use this tool responsibly and at your own risk.


## 🚀 Prerequisites

Before working with this project, make sure you have [uv](https://docs.astral.sh/uv/) installed. 👉 Install guide: [uv docs](https://docs.astral.sh/uv/getting-started/installation/)

If you are a developer and want to contribute to this project, you may want to have 
[make](https://www.gnu.org/software/make/) installed as well.


## ⚡ Installation

Install dependencies into a local virtual environment:

```bash
uv sync --all-groups
```

Then, to activate the virtual environment:

On Linux / macOS:

```bash
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
# If your PowerShell execution policy prevents running the script, run:
powershell -ExecutionPolicy Bypass -File .venv\Scripts\Activate.ps1
```

On Windows (CMD):

```cmd
.venv\Scripts\activate.bat
```

## 🛠️ Usage

### Create your own figure

Create a new FABA figure from a folder containing MP3 files. The target figure must 
not already exist in the FABA library, otherwise the command will fail to avoid 
accidental overwrites.

For example, to create a new FABA figure with ID `4742` using the songs in `/home/user/songs` 
and copy it to the FABA box mounted at `/mnt/faba/MKI01`, run:

```bash
openfaba insert \
  --figure-id 4742 \
  --source /home/user/songs \
  --faba-library /mnt/faba/MKI01
```

Write an NFC TAG with the figure ID and enjoy it! If you need help on how todo it, 
[these FAQs](https://github.com/wansors/myfaba-hacks/blob/main/FAQ.md) from the original 
wansors' project have a lot of useful information.

### Add songs to an existing figure

Append additional MP3 files to an already existing figure. New tracks are added after the 
existing ones and never overwrite previously stored audio.

```bash
openfaba extend \
  --figure-id 4742 \
  --source /home/user/new_songs \
  --faba-library /mnt/faba/MKI01
```


### Replace a figure

Delete an existing figure and recreate it from scratch using a new set of MP3 files. This 
operation removes the previous contents of the figure.

```bash
openfaba replace \
  --figure-id 4742 \
  --source /home/user/songs \
  --faba-library /mnt/faba/MKI01
```


### Listen to some FABA songs on your computer

Extract (deobfuscate) a single figure from a FABA box and convert it back to standard MP3 
files so they can be played on a computer or mobile device.

For example, to extract the Italian red elephant **Ele** (figure ID `0010`):

```bash
openfaba extract \
  --figure-id 0010 \
  --faba-library /mnt/faba/MKI01 \
  --output /home/user/elephant_ele
```


### Obfuscate an entire MP3 library

Convert a directory tree of MP3 files into a FABA-compatible MKI library. Subfolders named 
`K####` are interpreted as figure IDs; otherwise a default figure ID is used.

```bash
openfaba obfuscate \
  --mp3-library /home/user/mp3_library \
  --faba-library /mnt/faba/MKI01
```


### Deobfuscate an entire FABA library

Convert all figures from a FABA MKI library back into MP3 files, preserving the original 
folder structure.

```bash
openfaba deobfuscate \
  --faba-library /mnt/faba/MKI01 \
  --mp3-library /home/user/output_mp3
```

## 🪙 Resources used to create this project

- [myfaba-hacks GitHub repository](https://github.com/wansors/myfaba-hacks)
- [Hacking MyFaba Medium Article](https://medium.com/@wansors/hacking-myfaba-an-educational-journey-into-storytelling-box-customization-cc6fc5db719d)
- [Myfaba Store](https://www.myfaba.it/prodotti-sonori/acquista-per-tipologia/personaggi-sonori/)


## 📦 Tools for Developers

Common development tasks are wrapped in the `Makefile` for convenience.

### Linting, Formatting, and Type Checking

```bash
make qa
```

Runs **Ruff** for linting and formatting, and **Mypy** for type checking.

### Running Unit Tests

Before running tests, override any required environment variables in the `.env.test` file.

```bash
make test
```

Executes the test suite using **Pytest**.

### Building the Project

```bash
make build
```

Generates a distribution package inside the `dist/` directory.

### Cleaning Up

```bash
make clean
```

Removes build artifacts, caches, and temporary files to keep your project directory clean.

### Updating project version

```bash
make version
```

Interactively prompts you to select the type of version update to apply (major, minor, patch, tag) 
and automatically updates the project version accordingly.


## 🤝 Contributing

Contributions are welcome!
Please ensure all QA checks and tests pass before opening a pull request.

---

<sub>🚀 Project starter provided by [Cookie Pyrate](https://github.com/gvieralopez/cookie-pyrate)</sub>
