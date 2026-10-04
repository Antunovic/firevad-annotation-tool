# Fire-VAD alat za anotaciju

[![Testovi](https://github.com/Antunovic/firevad-annotation-tool/actions/workflows/tests.yml/badge.svg)](https://github.com/Antunovic/firevad-annotation-tool/actions/workflows/tests.yml)

Alat za tekstualno anotiranje videozapisa iz fire-VAD dataseta (RGB i termalna/IR kamera).
Radi na Windowsu, macOS-u i Linuxu. *English: [README_EN.md](README_EN.md).*

## 1. Preuzimanje

1. **Alat:** [firevad-annotation-tool-main.zip](https://github.com/Antunovic/firevad-annotation-tool/archive/refs/heads/main.zip)
   (ili na vrhu ove stranice: zeleni gumb **Code** → **Download ZIP**).
2. **Videozapisi:** `test_VAD.zip` (oko 3 GB); link na Google Drive dobit ćeš od koordinatora projekta.
   Google Drive upozori da tako veliku datoteku ne može provjeriti na viruse;
   klikni **Download anyway**.
3. Raspakiraj **oba** ZIP-a u istu mapu, npr. u *Preuzimanja* (Downloads):

   ```text
   Downloads/
     firevad-annotation-tool-main/    ← alat
     test_VAD/                        ← videozapisi
       environment_1/
       environment_2/
       ...
   ```

   - **Windows:** desni klik na ZIP → **Extract All…** (*Izdvoji sve…*) → **Extract**.
     Savjet: prije raspakiravanja desni klik na ZIP → **Properties**, označi **Unblock**
     i klikni **OK**. Tada Windows kasnije ne prikazuje sigurnosna upozorenja za alat.
   - **macOS:** dvoklik na ZIP (Safari ga obično raspakira sam).

   Dodatne mape koje nastanu raspakiravanjem (npr. `test_VAD\test_VAD\`) nisu problem.
   Ako alat ne pronađe videozapise, pitat će te gdje su.

## 2. Pokretanje

Prvo pokretanje traje minutu-dvije i treba internet: alat u svoju mapu `.venv-annotator`
instalira Python pakete numpy i Pillow. U sustav se ne instalira ništa osim Pythona,
i to samo ako ga nema. Kasnije alat radi i bez interneta.

### Windows

1. U mapi alata dvoklikni **`run_windows.bat`**.
2. Ako se pojavi upozorenje *Windows protected your PC*, klikni **More info** pa **Run anyway**.
   Kod upozorenja *Open File – Security Warning* klikni **Run**.
3. Ako na računalu nema Pythona, skripta ponudi da ga instalira: pritisni **Y**.
   Ako to ne uspije, instaliraj Python 3.13 sa [python.org](https://www.python.org/downloads/windows/)
   (*Windows installer (64-bit)*, zadane postavke) i ponovno pokreni `run_windows.bat`.
4. Crni prozor ostavi otvoren dok radiš.

### macOS

1. U mapi alata dvoklikni **`run_mac.command`**.
2. Ako macOS javi da datoteku ne može otvoriti (*Apple could not verify…* ili
   *unidentified developer*), zatvori poruku, pa:
   - na macOS-u 15 i novijem: **System Settings** → **Privacy & Security**, pri dnu kod
     *run_mac.command* klikni **Open Anyway** i potvrdi;
   - na starijem macOS-u: desni klik (Control-klik) na `run_mac.command` → **Open** → **Open**.

   Može i bez upozorenja: otvori aplikaciju **Terminal**, upiši `bash ` (s razmakom na kraju),
   povuci `run_mac.command` u prozor Terminala i pritisni **Enter**.
3. Ako na Macu nema odgovarajućeg Pythona, otvorit će se python.org: preuzmi i instaliraj
   *macOS 64-bit universal2 installer*, pa ponovno pokreni `run_mac.command`.
4. Ako macOS pita smije li Terminal pristupiti mapi *Downloads*, klikni **Allow**.
   Prozor Terminala ostavi otvoren dok radiš.

### Linux

U terminalu, u mapi alata, pokreni `bash run_linux.sh`.
Potreban je Python 3 s Tk-om i venv-om, npr. na Ubuntuu/Debianu:
`sudo apt install python3 python3-tk python3-venv`.

## 3. Prvo pokretanje

- Upiši svoje **ime i prezime**. Njime su označene sve tvoje anotacije, zato ga uvijek
  piši jednako. Alat ga pamti; možeš ga promijeniti gumbom **Change annotator…**.
- Alat sam pronađe mapu `test_VAD`. Ako je ne nađe, odaberi mapu u koju si raspakirao
  `test_VAD.zip`. Kasnije je možeš promijeniti gumbom **Change dataset folder…**.

## 4. Anotiranje

1. Odaberi scenu i klikni **Open scene** (ili dvoklik na scenu).
2. Prikazana su tri sinkronizirana videa:
   - **RGB**: obični video,
   - **IR – relative**: termalna slika s kontrastom prilagođenim svakom frameu (dobro se vide oblici),
   - **IR – absolute**: termalna slika na stalnoj temperaturnoj skali (raspon upiši u
     **Abs. range (°C)** ili klikni **Video range** za raspon cijelog videa).

   Kad je miš iznad IR prikaza, vidiš temperaturu u °C.
3. **Segmenti:** zaustavi video na frameu u kojem počinje novi segment i pritisni **B**.
   Novi segment počinje kad se nešto pojavi ili nestane sa scene ili kad osoba promijeni
   radnju. Segmenti se nižu jedan za drugim i pokrivaju cijeli video.
4. **Opisi:** za svaki segment (odaberi ga u popisu lijevo) napiši četiri kratka opisa
   **na engleskom**:

   | Polje | Što opisati |
   |---|---|
   | 1. RGB initial state | početno stanje: relevantni objekti i osobe te gdje se nalaze |
   | 2. Dynamics in RGB | radnje, pojave i promjene tijekom segmenta (samo RGB) |
   | 3. IR initial state | što je na početku segmenta toplije ili hladnije od okoline i gdje |
   | 4. Dynamics in IR | raste li, pada li ili miruje temperatura; širi li se ili skuplja toplije područje |

   Opisuj objektivno, samo ono što se vidi: bez tumačenja opasnosti i namjera ljudi te
   bez neodređenih riječi poput *slightly*, *slowly* ili *rapidly*. Ne pozivaj se na
   prethodne segmente. Gumbi uz polja upisuju standardne rečenice (npr. **No changes**).
   Detaljne upute su u alatu: **Boundary instructions…** i **Caption instructions…**.
5. Spremi s **Ctrl+S** (na Macu **Cmd+S**). Nedovršen rad možeš spremiti i nastaviti kasnije.

| Tipka | Radnja |
|---|---|
| Space | play / pauza |
| ← / → | jedan frame natrag / naprijed |
| ↑ / ↓ | 10 frameova natrag / naprijed |
| B | novi segment počinje na ovom frameu |
| Delete | ukloni početnu granicu odabranog segmenta |
| F1 | pomoć |

## 5. Slanje anotacija

1. U glavnom prozoru klikni **Export all my annotations**, a zatim **Yes** da se otvori mapa.
2. Pošalji datoteku **`combined_export.json`** koordinatoru projekta.

Anotacije se spremaju u mapu alata, u `annotations/<tvoje_ime>/`. Ne briši tu mapu.

## 6. Nova verzija alata

1. Preuzmi i raspakiraj novu verziju alata (vidi 1. korak). Staru mapu još ne briši.
2. Iz stare mape alata kopiraj u novu mapu **`annotations`** i datoteku **`annotator_config.json`**.
3. Pokreni novu verziju i provjeri jesu li tvoje anotacije tu. Tek tada obriši staru mapu.

## Problemi

| Problem | Rješenje |
|---|---|
| Na Macu se otvori prazan (bijeli) prozor | Pokreni alat preko `run_mac.command`, a ne naredbom `python3 annotate_gui.py`. Ako ne pomogne, instaliraj Python 3.13 s python.org. |
| *annotate_gui.py not found* | ZIP nije raspakiran. Raspakiraj ga (1. korak) i pokreni alat iz raspakirane mape. |
| *No fire-VAD videos were found* | Raspakiraj `test_VAD.zip` i odaberi raspakiranu mapu. |
| Instalacija numpy/Pillow ne uspije | Provjeri internetsku vezu i pokreni ponovno. Ako i dalje ne radi, instaliraj Python 3.13 i obriši mapu `.venv-annotator` u mapi alata (na Macu skrivene mape prikazuje **Cmd+Shift+.**). |
| Nešto drugo | Pošalji koordinatoru snimku zaslona crnog prozora (Windows) ili Terminala (macOS). |

Za developere (testovi, CI, alati za dataset): [README_EN.md](README_EN.md#for-developers).
