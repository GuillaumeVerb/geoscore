# Calibration cal-02 — plan ciblé (prêt pour analyse des exports)

Ce document fixe le **plan d’implémentation** pour une passe **cal-02**, alignée sur `scoring-engine-v1.md`, `rules-catalog-v1.md`, `recommendations-mapping.md` et les anomalies déjà listées dans `calibration.md`.  
**À valider** contre tes exports réels (`calibration/out/*.json` / `.md`) : ajuster les seuils numériques marqués *(à caler sur données)*.

---

## 1. Objectifs produit (rappel)

| Priorité | Objectif cal-02 |
|----------|-------------------|
| P1 | Moins de faux positifs **SPA** sur **liens internes** |
| P2 | Moins de pénalités agressives sur **articles / longform** |
| P3 | **Partial** → ne pas afficher un **GEO** / **confiance** trop optimistes |
| P4 | Moins de **répétitions** de recommandations (même famille) |
| P5 | Garder des **scores lisibles** (SEO / GEO / global inchangés en structure) |

Contraintes : déterministe, pas de LLM, pas de YAML engine, pas de Celery/Redis, **petits diffs** dans le code existant.

---

## 2. Fichiers qui seront touchés

| Fichier | Rôle |
|---------|------|
| `backend/app/services/pipeline/score_minimal.py` | Règles, poids, caps, fusion reco, lecture `pipeline_context` |
| `backend/app/services/pipeline/orchestrator.py` | Injecter `pipeline_context` dans le dict passé au scoring (ou dans `extraction` avant score) |
| `backend/app/services/pipeline/extract_step.py` | *Optionnel* — ne dupliquer que si on préfère stocker le contexte dans `extraction` au build ; sinon **seulement orchestrator** |
| `backend/app/services/pipeline/constants.py` | Bump `scoring-v1-cal02` / `ruleset-v1-cal02` |
| `backend/tests/test_score_calibration.py` (+ éventuellement `test_extraction_scoring.py`) | Tests sur SPA flag, article, partial |
| `docs/03-build/calibration.md` | Section « cal-02 appliqué » une fois mergé |

**Pas** de changement API HTTP.

---

## 3. Transport des signaux `is_probably_spa` / `fetch_method`

Aujourd’hui `run_deterministic_score` ne voit pas le fetch ORM. **Proposition cal-02** :

- Ajouter un bloc optionnel dans l’objet déjà passé au scoring, par ex.  
  `extraction["pipeline_context"] = { "partial": bool, "is_probably_spa": bool | None, "primary_fetch_method": str }`
- Rempli dans **`orchestrator.py`** au moment de l’appel à `run_deterministic_score` (et **`rescore_scan_only`** depuis `ScanFetchResult` + scan / payload extraction existant).
- **Offline calibration** : laisser absent ou `partial=False`, `is_probably_spa=None` → comportement actuel.

Cela évite une refonte des signatures tout en garde une seule source de vérité côté pipeline.

---

## 4. Changements proposés — règle par règle

### 4.1 SPA / liens internes (P1)

| ID | Règle actuelle (cal-01) | Cal-02 proposé | Justification |
|----|-------------------------|----------------|---------------|
| IL-SPA-1 | `INTERNAL_LINKS_THIN` si `word_count > 300` et `internal < 2` | Si `pipeline_context.is_probably_spa is True` : **ne pas émettre** l’issue tant que `internal >= 1` **ou** relever le seuil à `word_count > 500` **et** `internal < 1` | Les SPA comptent souvent mal les liens dans le HTML initial / navigation client |
| IL-SPA-2 | `seo_internal_links` score | Si SPA : multiplier le sous-score `seo_internal_links` par **0.88** (plancher 40) *sans* issue si `internal >= 1` | Évite double punition score + issue |
| IL-SPA-3 | `fetch_method == http_playwright_attempted` + limitation `PLAYWRIGHT_NO_GAIN` | Traiter comme signal « capture fragile » : appliquer le même assouplissement SPA **ou** le flag `is_probably_spa` si déjà true | Aligner avec les pages où le DOM final reste pauvre en ancres |

*(À caler sur données)* : si les exports montrent encore trop de faux positifs sur `docs_nextjs`, passer IL-SPA-1 à « skip issue SPA si `internal >= 0` et `external >= 5` » (docs avec beaucoup de liens sortants).

---

### 4.2 Articles / longform (P2)

| ID | Règle | Cal-02 proposé |
|----|--------|----------------|
| ART-1 | `MULTIPLE_H1` | Si `page_type == article` **et** `word_count >= 500` : **severity** `low`, **ne pas** appliquer `h_score = min(..., 68)` pour multi-H1 ; ou **skip** l’issue si `h2_count >= 3` *(à caler)* | Les CMS presse / MDX dupliquent parfois des blocs |
| ART-2 | `H2_MISSING_ON_LONG_PAGE` | Si `article` : seuil `word_count > 650` (au lieu de 520 global) | Longform sans H2 fréquent sur certains templates |
| ART-3 | `FAQ_ANSWERABILITY_WEAK` | Si `article` : seuil `word_count > 650` **ou** désactiver si `how_what_why_heading_count >= 1` déjà présent | Moins d’incitation FAQ sur éditorial |
| ART-4 | `CITATION_SIGNALS_WEAK` | Si `article` **et** `word_count > 800` **et** `list_item_count >= 5` : ne pas émettre *(à caler)* | Listes = extractabilité déjà partielle |

Ne **pas** assouplir `pricing_page` / `landing_page` sur offre / hero dans cette passe (lisibilité produit).

---

### 4.3 Partial → confiance & GEO (P3)

| ID | Comportement actuel | Cal-02 proposé |
|----|---------------------|----------------|
| PC-1 | `partial` → limitation + `conf_numeric -= 0.12` | Ajouter **`conf_numeric -= 0.05`** supplémentaire si **à la fois** `partial` **et** (`is_probably_spa` **ou** `primary_fetch_method` contient `playwright_attempted`) | Capture instable |
| PC-2 | `analysis_confidence` | Si `partial` **et** `word_count < 400` : **plafonner** le label à **`medium`** (ne jamais afficher `high`) | Éviter « high » sur contenu incertain |
| PC-3 | `geo_score` agrégé | Après calcul GEO : si `partial`, appliquer **`geo_score = min(geo_score, 85)`** *(à caler 80–88)* | GEO plus sensible au rendu que SEO sur partial |
| PC-4 | Sous-scores GEO | Option plus fine : multiplier **`hero_clarity`** et **`extractability`** par **0.94** si `partial` (pas `trust_entity`) | Réduit l’optimisme sans écraser la confiance entité |

**Global** : `global_score = 0.5 * seo + 0.5 * geo` inchangé ; l’effet passe par GEO cap / sous-scores.

---

### 4.4 Recommandations — moins de répétition (P4)

| ID | Mécanisme | Cal-02 proposé |
|----|-----------|----------------|
| RC-1 | `_dedupe_recommendations` par `key` | Conserver |
| RC-2 | Familles mapping doc | Après dédup : si **à la fois** `REWRITE_HERO` et `CLARIFY_OFFER_POSITIONING` : **garder une seule** — priorité min ; titre unifié du type « Clarifier le message au-dessus de la ligne de flottaison » ; `explanation` = 2 phrases fusionnées courtes | Aligné `recommendations-mapping.md` (éviter 2 reco marketing |
| RC-3 | `IMPROVE_HEADING_STRUCTURE` | Si **deux issues** distinctes (ex. `H1_MISSING` + `H2_MISSING_ON_LONG_PAGE`) mènent à la **même key** : une seule entrée (déjà le cas si même key) ; sinon forcer **une seule** reco heading avec **priority = min** | Réduit doublons de titres différents pour le même key |
| RC-4 | Plafond produit | Trier par priority et **tronquer à 6** recommandations en sortie API *(optionnel, breaking UX si le front attend tout)* — **recommandation** : ne pas tronquer API en cal-02 ; **tronquer seulement** dans l’export calibration / doc produit ; si troncature API souhaitée plus tard, versionner | Évite surprise front |

Implémentation légère cal-02 : **RC-2 + RC-3** dans une fonction `_merge_recommendation_families(recs: list[Recommendation])` appelée après `_dedupe_recommendations`.

---

### 4.5 Caps / garde-fous transverses

| ID | Garde-fou |
|----|-----------|
| CAP-1 | Tout nouveau seuil **SPA** ne s’applique que si `is_probably_spa is True` (pas `None` en offline) pour ne pas changer les pages « classiques » |
| CAP-2 | Plancher **global** optionnel : `global_score = max(global_score, 28)` si `fetch_ok` et `word_count > 200` — **hors cal-02 par défaut** (risque de masquer de vrais échecs) ; ne l’activer que si les exports le justifient |
| CAP-3 | Documenter dans `calibration.md` les numéros finaux après lecture des JSON |

---

## 5. Impact attendu par type de page (hypothèses)

| Page | Contexte | Effet principal attendu |
|------|----------|-------------------------|
| **docs_react** | JS-heavy, souvent beaucoup de liens client / shell | Moins d’`INTERNAL_LINKS_THIN` si `is_probably_spa` ; GEO un peu plus prudent si `partial` (offline) ou PW no-gain |
| **docs_nextjs** | Idem + longues pages doc | ART / SPA comme react ; H2/FAQ moins agressifs si typé `article` |
| **landing_linear** | Landing commerciale | Peu de changement voulu sur **offre / hero** ; reco fusionnées peuvent **réduire** le bruit si hero + offre déclenchent tous les deux |
| **Pricing** (ex. Stripe) | `pricing_page` | Pas d’assouplissement article ; possible légère baisse de confiance si `partial` + capture fragile uniquement |
| **Article éditorial** | Longform | Moins de `MULTIPLE_H1` / FAQ / citation injustifiés ; scores SEO structure un peu plus stables |

**Important** : sans tes fichiers `calibration_*.json`, les seuils **ART-*** et **PC-3** restent des **propositions** ; l’analyse des exports peut les décaler de ±50–100 mots ou ajuster le cap GEO (80 vs 85).

---

## 6. Comment tu m’utilises après tes runs

1. Dépose ou colle le **JSON** (ou le tableau MD) des deux modes **offline** vs **api** pour les lignes qui t’intéressent (au minimum : `docs_react`, `docs_nextjs`, `landing_linear`, une pricing, un article).  
2. Indique pour chaque ligne : **« score trop haut / trop bas »** et **« issue/reco à tort »** en une phrase.  
3. J’affine les constantes *(à caler sur données)* et je propose le **diff minimal** sur `score_minimal.py` + `orchestrator.py` + tests.

---

## 7. Prochaine étape après cal-02

- Regénérer **deux exports** (avant/après cal-02) et les archiver dans `calibration/out/`.  
- Si stable : figer une **ligne directrice produit** (1 paragraphe par famille de page dans `calibration.md`).  
- Ensuite seulement : **LLM** borné ou **queue** — pas avant que les scores/docs/landing soient validés manuellement sur 15–20 URLs.
