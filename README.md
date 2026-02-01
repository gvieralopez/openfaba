# openFABA

**openFABA**  converts regular MP3 files into the special format used by the FABA storytelling
box and also lets you extract playable MP3s back from a FABA device. This project builds upon the 
reverse-engineering work by [wansors](https://github.com/wansors/myfaba-hacks/blob/main/python/redele.py).
At the moment, **openFABA** supports **only the original FABA device**.


> 🚨 **Disclaimer — Use responsibly**
>
> **openFABA** is an independent project and is **not affiliated with or endorsed by FABA**.
> This software is provided *as is*, with no warranties.
>
> You are responsible for how you use this tool and for any consequences that may arise,
> including device malfunction or account-related actions. Some features may conflict
> with FABA’s terms of service or usage policies.
>
> This project aims to simplify the creation of custom, FABA-compatible figures and to
> personalize figures you already own. We do **not** endorse piracy, copyright 
> infringement, or misuse that could negatively impact FABA or its ecosystem. 
> Please support FABA by purchasing their products.


## Quick start

Make sure you have Python 3.13 or higher and install the tool from PyPI:

```bash
pip install openfaba
```

If you are a developer, want to run tests, install from source or follow developer
instructions see the developers guide: [DEVELOPERS.md](DEVELOPERS.md)

## Usage

**openFABA** supports the following commands:

- `insert` — create a new figure from MP3s and add to a FABA library
- `extend` — add songs to an existing figure (appends; never overwrites)
- `replace` — remove and recreate a figure's songs from a new set of MP3s
- `extract` — deobfuscate all songs from a figure back into MP3 files
- `obfuscate` / `deobfuscate` — convert entire libraries to/from FABA format

Next, you can find an example of usage for each of them.

### Create a new figure:

Create a new FABA figure from a folder containing MP3 files. The target figure must 
not already exist in the FABA library, otherwise the command will fail to avoid 
accidental overwrites.

For example, to create a new FABA figure with ID `4742` using the songs in `/home/user/songs` 
and copy it to the FABA box mounted at `/mnt/faba/MKI01`, run:

```bash
openfaba insert --figure-id 4742 --source /home/user/songs --faba-library /mnt/faba/MKI01
```

Write an NFC TAG with the data 02190530**4742**00 and enjoy it! If you need help on how todo it, 
[these FAQs](https://github.com/wansors/myfaba-hacks/blob/main/FAQ.md) from the original 
wansors' project have a lot of useful information.

### Add songs to an existing figure:

Append additional MP3 files to an already existing figure. New tracks are added after the 
existing ones and never overwrite previously stored audio.

```bash
openfaba extend --figure-id 4742 --source /home/user/new_songs --faba-library /mnt/faba/MKI01
```

### Replace a figure completely:

Delete an existing figure's sounds and recreate them from scratch using a new set of MP3 
files. This operation removes the previous contents of the figure.

```bash
openfaba replace --figure-id 4742 --source /home/user/songs --faba-library /mnt/faba/MKI01
```

### Listen to some FABA songs from a given figure on your computer:

Extract (deobfuscate) a single figure from a FABA box and convert it back to standard MP3 
files so they can be played on a computer or mobile device.

For example, to extract the Italian red elephant **Ele** (figure ID `0010`):

```bash
openfaba extract --figure-id 0010 --faba-library /mnt/faba/MKI01 --output /home/user/elephant_ele
```

### Deobfuscate a FABA library back to MP3s:

Convert all figures from a FABA MKI library back into MP3 files, preserving the original 
folder structure.

```bash
openfaba deobfuscate --faba-library /mnt/faba/MKI01 --mp3-library /home/user/output_mp3
```

### Obfuscate a whole MP3 library into MKI structure:

Convert a directory tree of MP3 files into a FABA-compatible MKI library. Subfolders named 
`K####` are interpreted as figure IDs; otherwise a default figure ID is used.

```bash
openfaba obfuscate --mp3-library /home/user/mp3_library --faba-library /mnt/faba/MKI01
```

## Roadmap

- **Add a CSV with figure metadata** — provide a machine-readable `figures.csv` that lists
	each figure ID, name, language, source URL and other metadata for either users and tools 
	reference.
- **Add a `details` command** — add a `openfaba details <figure-id>` command
	that looks up and prints human-friendly metadata from the CSV (name, tracks,
	language, notes, and source link).
- **Auto-update script (scraper)** — include a script that can periodically fetch
	metadata from MyFaba and update `figures.csv`; documented in `DEVELOPERS.md`.
- **Multi-device support (FABA+)** — plan and expose an abstraction layer so the
	obfuscation/deobfuscation pipeline can target multiple FABA-compatible devices
	(different file layouts or obfuscation).
- **UI** — explore a small GUI with similar functionality of current CLI.

---

## Resources

- [myfaba-hacks GitHub repository](https://github.com/wansors/myfaba-hacks)
- [Hacking MyFaba article](https://medium.com/@wansors/hacking-myfaba-an-educational-journey-into-storytelling-box-customization-cc6fc5db719d)
- [Myfaba Store](https://www.myfaba.it/prodotti-sonori/acquista-per-tipologia/personaggi-sonori/)


---

If you'd like the full developer guide (installation from source, tests, linters,
and build steps), open [DEVELOPERS.md](DEVELOPERS.md).
