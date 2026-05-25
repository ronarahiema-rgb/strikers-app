# Teamafspraken & Git/GitLab Workflow — Team Strikers (BrainBoost)

Binnen ons projectteam is Git de basis van hoe we samenwerken. Om te voorkomen dat we elkaars code per ongeluk overschrijven, ingewikkelde merge-conflicts krijgen of het overzicht verliezen, hebben we deze werkafspraken opgesteld. Zo houden we de code van het BrainBoost Dashboard overzichtelijk en weet iedereen precies wat er in elke fase van het project wordt verwacht.


1. De Stappen van de Workflow (Board Fases)

Ons GitLab-board is opgedeeld in vaste, opeenvolgende kolommen. Een User Story of Issue doorloopt verplicht dit volledige proces van start tot finish:

[1. Open] ──> [2. Doing] ──> [3. Verify] ──> [4. Feedback Verwerken] ──> [5. Merge] ──> [6. Closed]


### Stap 1: Open (Nog niet aan begonnen)
* Alle geplande functionaliteiten, taken en bugs staan als afzonderlijke Issues in deze kolom.
* Een Issue bevat altijd een duidelijke omschrijving en een koppeling naar de betreffende deeltaak Zowel als acceptatie criteria, labels en een assignee

### Stap 2: Doing (In Progress)
* Zodra je aan een taak begint, versleep je het Issue naar Doing.
* Je koppelt jezelf (Assignee) aan het Issue, zodat het team ziet wie ermee bezig is.
* **Branching-regel (HvA Flow):** Je maakt direct een eigen *feature branch* aan vanuit de actuele `main` branch. 
    * *Format:* `feature/issue-[nummer]-[korte-beschrijving]` (bijv. `feature/issue-12-wachtwoord-vergeten`).
    * *Afspraak:* Werk in kleine, kortlevende branches. Voorkom dat je wekenlang op dezelfde branch blijft werken.

### Stap 3: Verify (Code Review & Kwaliteitscontrole)
* Is de code af en lokaal getest? Dan push je de branch en open je in GitLab een Merge Request (MR) naar de hoofdbranch. Je verplaatst het Issue naar **Verify**.
* Geen directe merges: Het is ten strengste verboden om rechtstreeks in `main` te mergen of te pushen. Alles loopt via een MR.
* Eerlijke verdeling: Code reviews worden eerlijk binnen het team verdeeld. Er wordt geroteerd, zodat niet steeds dezelfde persoon alle reviews hoeft te doen.

### Stap 4: Feedback Geven & Verwerken
* De reviewer controleert de code kritisch op basis van onze kwaliteitsrichtlijnen (zie sectie 3) en laat concrete opmerkingen achter.
* De ontwikkelaar verwerkt de feedback op dezelfde branch en pusht de aanpassingen.

### Stap 5: Merge
* Als de reviewer akkoord is en alle discussiepunten zijn opgelost, krijgt de code de status 'Approved'. 
* De branch wordt samengevoegd met de hoofdbranch op de daarvoor afgesproken momenten.

### Stap 6: Closed (Done)
* De code staat veilig in de hoofdbranch, de feature branch wordt automatisch verwijderd en het Issue wordt definitief gesloten.


2. Commit Conventions (HvA / Conventional Commits)

Om de geschiedenis van ons project leesbaar en traceerbaar te houden, gebruiken we verplicht Conventional Commits. Elke commit message moet opgebouwd zijn volgens het format: `type(scope): duidelijke en concrete beschrijving`.

* `feat`: Een nieuwe functionaliteit voor de applicatie.
    * *Bijvoorbeeld:* `feat(auth): voeg applicatiewachtwoord reset toe voor gmail`
* `fix`: Het oplossen van een bug of fout in de code.
    * *Bijvoorbeeld:* `fix(dashboard): verwijder stippellijnen uit chartjs grid`
* `docs`: Wijzigingen in documentatie, zoals de README of comments.
    * *Bijvoorbeeld:* `docs(readme): update installatie-instructies voor venv`
* `style`: Aanpassingen aan het uiterlijk of de formattering (CSS/linter) zonder dat de logica verandert.
    * *Bijvoorbeeld:* `style(dashboard): pas grid-column layout aan naar symmetrische grid`



3. Richtlijnen voor het Reviewen & Feedback Geven

Een Code Review is geen aanval, maar een kwaliteitsfilter en een leermoment voor het hele team. Feedback moet zo concreet en helder zijn geschreven dat iemand die niet in het projectteam zit, het ook direct zou snappen.

Hoe geef je constructieve feedback? (Concreet & Advisered)
1.  Formuleer als advies, voorstel of vraag: Schrijf feedback nooit dwingend of verwijtend. Probeer de programmeur aan het denken te zetten of een alternatief voor te stellen.
    * *Fout (Te vaag/bot):* "Dit klopt niet, verander dit."
    * *Goed (Constructief/Advies):* "Ik zie dat je hier een f-string gebruikt voor de SQL-query. Zouden we hier niet beter een geparametriseerde query van kunnen maken om SQL-injectie te voorkomen?"
2.  Geef concrete voorbeelden bij criteria: Als je vraagt om iets aan te passen, geef dan direct een codevoorbeeld of een duidelijke verwijzing naar hoe het beter kan.
    * Bijvoorbeeld: "Voor de leesbaarheid van de Chart.js options raad ik aan om de gridlines onzichtbaar te maken via `grid: { display: false }`. Dit zorgt voor een strakker dashboard. Zie dit voorbeeld: [code-snippet]."
3. Controleer expliciet op Code Kwaliteit:
    * Is de code veilig (geen hardgecodeerde wachtwoorden/API keys, geen SQL-injectie risico's)?
    * Is er dubbele code aanwezig die in een hulpfunctie (zoals in `DocentHome` of utility functies) kan worden ondergebracht?
    * Zijn variabelen en functies logisch en in het Nederlands/Engels (consistent conform teamafspraak) benoemd?

Het verwerken van feedback:
* Resolve Thread: Nadat de ontwikkelaar de feedback heeft aangepast in de code en opnieuw heeft gepusht, drukt de ontwikkelaar of reviewer op de knop "Resolve thread" in GitLab. Pas als alle threads zijn opgelost ('resolved'), kan de Merge Request worden goedgekeurd.



 4. Tijdschema & Planning (Realistische Afspraken)

Om de vaart in het project te houden en te voorkomen dat iedereen op het allerlaatste moment voor de deadline gaat mergen, hanteren we een strak wekelijks schema:

* Vaste dag voor Verify (Reviewen): Elke [Kies vaste dag, bijv. dinsdag] controleren en reviewen we elkaars openstaande Merge Requests grondig.
* Volgende dag Mergen: De daaropvolgende dag, op [Kies dag, bijv. woensdag], worden alle goedgekeurde en foutloze Merge Requests daadwerkelijk samengevoegd met de hoofdbranch.
* Wekelijkse Merge Deadline: Er is een vaste wekelijkse merge-moment aan het einde van de sprintweek om te zorgen dat we altijd een stabiele, werkende live-versie van het BrainBoost Dashboard hebben draaien.
* Wie voert de merge uit? De reviewer die de laatste goedkeuring (Approval) geeft, is verantwoordelijk voor het indrukken van de Merge-knop, tenzij vooraf expliciet is afgesproken dat de lead developer dit doet om eventuele merge-conflicts centraal op te lossen.



5. Afbakening: Code Kwaliteit vs. Acceptatiecriteria

Het is van cruciaal belang dat we de code-afspraken in de SLA en dit Git-document zuiver scheiden van de functionele acceptatiecriteria van de user stories:

* Acceptatiecriteria (Functioneel): Dit beschrijft wat de applicatie moet doen voor de eindgebruiker. (Bijvoorbeeld: "De docent moet via een zoekbalk de leerlingenlijst kunnen filteren op voor- en achternaam.") Dit testen we functioneel.
* Code Kwaliteit Criteria (Technisch): Dit beschrijft hoe de code is opgebouwd onder de motorkap. (Bijvoorbeeld: "De code mag geen inline JavaScript bevatten, moet voldoen aan OOP-pijlers waar toepasbaar, mag geen onnodige stippellijnen tonen in grafieken, en mag geen SQL-injectie kwetsbaarheden bevatten.") Dit controleren we tijdens de Verify-fase in de GitLab Merge Request.



Ieder teamlid wordt geacht zich strikt aan deze stappen te houden. Bij afwijkingen spreken we elkaar constructief aan tijdens de stand-ups.