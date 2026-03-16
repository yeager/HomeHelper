# HomeHelper

Visuella steg-för-steg instruktioner för hushållssysslor.

## Funktioner

- **Sysslor**: Diska, tvätta, städa, laga mat
- **Steg-för-steg**: Tydliga instruktioner med checkboxar
- **Timer**: Inbyggd nedräkning för steg som behöver det
- **Progress**: Sparar din framgång automatiskt

## Installation

### Krav

- Python 3.8+
- PyGObject (GTK4 + libadwaita)

### Ubuntu/Debian

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
pip install .
```

### Fedora

```bash
sudo dnf install python3-gobject gtk4 libadwaita
pip install .
```

### Kör utan installation

```bash
python -m homehelper.app
```

## Licens

MIT
