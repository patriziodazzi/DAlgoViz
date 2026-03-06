# DAlgoViz

> Visualizzatore interattivo di algoritmi distribuiti e leggi di scalabilità.

Tool Python standalone. Si installa con `pip install .` e si lancia con `dalgoviz`.

## Moduli v0.1

| Modulo | Contenuto |
|--------|-----------|
| **Leggi di scalabilità** | Amdahl, Gustafson, USL, Little's law |
| **Lamport clocks** | Diagramma spazio-tempo, happens-before |
| **Vector clocks** | Vettori per processo, eventi concorrenti |
| **Raft** | Election, term, heartbeat, log replication |
| **Mutual exclusion** | Ricart-Agrawala / token ring |
| **Deadlock** | Wait-for graph, formazione ciclo |
| **2PC** | Prepare/commit/abort, failure coordinator |

## Uso

```bash
pip install .
dalgoviz
# Apre http://localhost:5000 nel browser
```
