# Release candidate (RC) — bug bash + URL pass

**Goal:** sortie très propre — **pas** de nouveau chantier feature, **pas** d’extension du scoring. Ne traiter que les problèmes **réellement gênants** pour un utilisateur réel.

**Prérequis:** déjà parcouru **`verify-deployment.md`** sur un environnement proche prod — notamment **Split deploy** (HTTPS, `CORS_ORIGINS` = origines front exactes, `NEXT_PUBLIC_API_URL` public sans slash final, Playwright sur l’API si activé) et la section **Full manual smoke** pour le déploiement réel.

---

## 1. Définition de « RC OK »

- Aucun **bloquant** sur les flux ci-dessous (crash, boucle infinie, données d’un autre user, public cassé).
- Au plus quelques **mineurs** documentés (cosmétique, wording) avec ticket post-release accepté.

---

## 2. Bug bash — flux critiques (ordre suggéré, ~45–60 min)

| # | Flux | Vérifier |
|---|------|----------|
| 1 | `/health` + `/ready` | Comportement attendu selon mock vs Postgres |
| 2 | `/` → lien **How scoring works** + **Example report** | Pas d’erreur console |
| 3 | Non connecté → soumission URL | Redirection sign-in + `returnTo` correct (y compris `#`) |
| 4 | Sign-in → dashboard | Liste / empty state ; pas de fuite entre comptes |
| 5 | Analyze URL réelle → `/scan/{id}` | Polling jusqu’à état final ; limitations visibles si partial |
| 6 | Session expirée ou 401 sur scan | Redirection sign-in (pas fallback mock silencieux sur création) |
| 7 | `/report/demo-example` (nav privée) | Contenu + note demo / offline OK |
| 8 | Rapport public réel | Fenêtre privée, sans token : charge et cohérence |
| 9 | Rescan + override page type (si temps) | Pas de régression évidente |

**À noter pour chaque bug:** URL, navigateur, capture ou extrait console, **repro en 3 étapes max**.

---

## Short V2 smoke test

Même périmètre que dans **`verify-deployment.md`** — uniquement **Projects** + **Compare to previous run** (lignée rescan). Pas de nouvelle feature ni changement d’API. Session connectée ; **Postgres** recommandé pour que les rescans et le `parent_scan_id` soient réalistes.

1. Sign in.
2. Create project.
3. Filter dashboard by project.
4. Create a new scan in that project.
5. Rescan from a result.
6. Open compare from result page.
7. Open compare from dashboard.
8. Verify safe 404 behavior for a scan without parent comparison (e.g. open `/scan/{id}/compare` for a scan that has no rescan parent — expect a controlled error, not a blank or crashed UI).

---

## 3. Pass manuel **5–10 vraies URLs**

Varier les **types de pages** (pas seulement la home). Exemples de gabarit — remplacer par des URLs que vous acceptez de tester :

| # | Type visé | URL testée | Résultat (OK / KO) | Commentaire si KO |
|---|-----------|------------|--------------------|---------------------|
| 1 | Homepage marketing | | | |
| 2 | Page pricing | | | |
| 3 | Article / blog long | | | |
| 4 | Doc / help (beaucoup de texte) | | | |
| 5 | Page « thin » ou très JS | | | |
| 6 | (optionnel) | | | |

**Critère:** seuls les KO **vraiment gênants** (confiance brisée, message faux, UX bloquée) justifient un correctif avant sortie. Le reste → backlog post-release.

---

## 4. Hors scope explicite (ne pas ouvrir en RC)

- Nouvelles features, scoring / ruleset, billing, gros refactors infra.
- Réécriture globale des libellés d’issues côté moteur (sauf erreur factuelle **évidente** et correctif minimal validé).

---

## 5. Références

- **`verify-deployment.md`** — garde-fous techniques + auth + démo + **Short V2 smoke test** (Projects + compare).
- **`release-readiness.md`** — matrice P0/P1, §4 (état implémenté), §1 (contexte historique uniquement).
- **`docs/00-product/post-release-backlog.md`** — idées volontairement reportées (hors scope RC).
- **`product-strengthening-plan.md`** — cadrage produit / crédibilité (déjà livré).

Quand les sections **2** (bug bash), **Short V2 smoke test**, et **3** (5–10 URLs) sont remplies avec **RC OK**, vous pouvez taguer / déployer la release candidate.
