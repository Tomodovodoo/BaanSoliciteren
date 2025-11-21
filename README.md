# BaanSoliciteren

Hai, ik ben Tom (21). Dit is mijn (semi-wetenschappelijke) zoektocht naar een baan, nu **met agents**.
Waarom zelf lijsten bijhouden als je een AI-agent hebt die je Gmail leest?

## Wat is er nieuw?

Ik heb een **lokale MCP server** voor Gmail opgezet en meerdere automatisering doorgezet. Het resultaat?

- **Agentic Job Tracking**: Mijn scripts praten nu direct met mijn inbox, met een geimplementeerde locale caching en email filtering, hoef ik niet teveel emails te lezen, en de emails die gelezen zijn, worden niet opnieuw gelezen.
- **Auto-Archive**: Afwijzing binnen? De agent gooit hem direct in het archief en de hele solicitatie ook.
- **Meer Vacatures**: Heb via webinstances onderzoek laten doen naar nieuwe banen, via GPT 5.1 Extended Thinking en Gemini 3 Pro. Zoeken kan ik. 50 banen in 15 minuten vinden kan ik niet.
- **Automatisch onderzoek**: Via alleen vacatures en een schema duidelijk information vergaren en in een .json zetten, cross-valideren, en daarna met een snelle manual review goedzetten.
- **PotentialSatisfaction 2.0**: Alles is opnieuw doorgerekend en geplot zodat ik weet waar ik als eerste bij wilt soliciteren
- **Deadlines checken**: En natuurlijk automatisch deadlines bekijken om te zien waar ik MOET soliciteren.

## De 3 metrics

- **Fit:** Kan ik het? (Of kan ik het leren zonder burn-out?)
- **Salary:** Bruto indicatie. Geld maakt niet gelukkig, maar geen geld is ook zo wat.
- **Preference:** Mijn onderbuikgevoel (0-10). De belangrijkste factor.

![Job ranking - PotentialSatisfaction](Baan_analyze/job_potential.png)

## Tech Stack

- **Python & JSON**: Geen databases, gewoon mappen en bestanden. Simpel en effectief. Heb hiervoor met .csv gewerkt en vindt ze toch minder leesbaar. Dit was vooral gemakkelijk.
- **Gmail MCP**: Lokale integratie voor real-time updates.
- **Automatic updates**: Ten alle tijden hoef ik alleen maar mijn emails automatisch te fetchen, agentically laten processen, en mijn solicitaties automatisch te updaten. Dit laat mij gewoon mijn motivatiebrieven schrijven, dat vind ik al moeilijk genoeg.

---

Vragen? Stuur een [email](mailto:tomthegreatest04@gmail.com)
