# Lokales Gedächtnis für Claude über Obsidian (Basic Memory)

Diese Anleitung richtet ein **persistentes, lokales Gedächtnis** für Claude ein,
das als ganz normale Markdown-Dateien in einem **Obsidian-Vault** liegt.

Verwendete Lösung: **[Basic Memory](https://github.com/basicmachines-co/basic-memory)**
(Open Source, MCP-Server). Claude schreibt/liest über MCP, du editierst dieselben
Dateien in Obsidian — beide Seiten bleiben synchron. Kein Cloud-Account, keine
API-Keys, alles bleibt lokal auf deinem Rechner.

---

## Warum Basic Memory?

- Speichert **plain Markdown** in einem Ordner (Standard: `~/basic-memory`),
  den du direkt als Obsidian-Vault öffnest.
- **Zwei-Wege-Sync**: Claude schreibt eine Notiz → taucht in Obsidian auf.
  Du korrigierst sie in Obsidian → Claude liest beim nächsten Mal die korrigierte
  Version.
- **Knowledge-Graph** über Wikilinks/`memory://`-Links, sichtbar in Obsidians
  Graph-View.
- **Suche**: Volltext + semantisch (Vektor).
- Funktioniert mit Claude Code, Claude Desktop, Cursor, VS Code u.a.

Alternativen (falls du nur Datei-Zugriff statt „Gedächtnis" willst):
- [iansinnott/obsidian-claude-code-mcp](https://github.com/iansinnott/obsidian-claude-code-mcp)
- [lstpsche/obsidian-mcp](https://github.com/lstpsche/obsidian-mcp)
- [bitbonsai/mcpvault](https://github.com/bitbonsai/mcpvault)
- [Piotr1215/mcp-obsidian](https://github.com/Piotr1215/mcp-obsidian)

---

## Voraussetzungen (auf deinem PC)

1. **uv** installiert (liefert `uvx`):
   - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. **Obsidian** installiert (https://obsidian.md).

> Hinweis: Diese Schritte laufen auf **deinem Rechner**. In einer Cloud-Session
> (Claude Code on the web) lässt sich der MCP-Server nicht dauerhaft betreiben,
> weil der Container nach der Session verworfen wird.

---

## Einrichtung

### Variante A — Claude Code (empfohlen für dieses Projekt)

Ein Befehl im Terminal:

```bash
claude mcp add basic-memory -- uvx basic-memory mcp
```

Oder projektbezogen über die mitgelieferte Vorlage: kopiere `.mcp.json.example`
zu `.mcp.json` (Claude Code fragt beim ersten Start, ob der Server vertraut wird):

```bash
cp .mcp.json.example .mcp.json
```

Prüfen:

```bash
claude mcp list
```

### Variante B — Claude Desktop

Datei `claude_desktop_config.json` öffnen
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`,
Windows: `%APPDATA%\Claude\claude_desktop_config.json`) und ergänzen:

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "uvx",
      "args": ["basic-memory", "mcp"]
    }
  }
}
```

Danach Claude Desktop neu starten.

---

## Mit Obsidian verbinden

1. Obsidian öffnen → **„Open folder as vault"**.
2. Den Ordner `~/basic-memory` auswählen (wird beim ersten Schreiben von Claude
   automatisch angelegt; du kannst ihn auch vorher manuell erstellen).
3. Fertig. Was Claude schreibt, erscheint als Notizen; der Graph-View zeigt die
   Verknüpfungen.

Eigenen Speicherort verwenden? Setze die Umgebungsvariable
`BASIC_MEMORY_PROJECT_ROOT` auf deinen gewünschten Vault-Pfad, bevor der Server
startet.

---

## Erster Test

In Claude (Code oder Desktop):

> „Merke dir: Mein TCG-Price-Tracker nutzt Playwright-Scraper für Cardmarket,
> Amazon, Idealo und Geizhals. Lege das als Notiz an."

Claude ruft dann `write_note` auf. Danach in Obsidian die neue Markdown-Datei
im Vault ansehen. In einer späteren Session:

> „Was weißt du über die Scraper meines Price-Trackers?"

Claude findet die Notiz per `search_notes` und nutzt sie als Kontext.

---

## Sicherheitshinweis

`.mcp.json` schaltet die Ausführung eines externen Pakets (`uvx basic-memory`)
scharf. Deshalb liegt hier bewusst nur eine **Vorlage** (`.mcp.json.example`),
die du nach eigener Prüfung selbst aktivierst. Aktiviere MCP-Server nur, wenn du
der Quelle vertraust.
