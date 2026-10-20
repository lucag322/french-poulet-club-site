# French Poulet Club — site

Site vitrine du French Poulet Club (Stockholm, ouverture printemps 2028). Une seule page statique, sans build : `index.html`, `img/`, `fonts/`.

## Aperçu local

```bash
python3 -m http.server 8766
```

Version suédoise, 404, robots et sitemap ne sont générés qu'à la construction :

```bash
python3 build.py --out _site --site http://localhost:8767 && python3 -m http.server 8767 -d _site
```

## Version suédoise

`sv/index.html` est produit par `build.py` à partir de `index.html` et de la liste `SV` (texte anglais → texte suédois). Un texte anglais modifié dans `index.html` doit l'être aussi dans `SV`, sinon la construction s'arrête en indiquant lequel.

## Mesure d'audience

Cloudflare Web Analytics (gratuit, sans cookie, donc sans bannière). Ajoutée en prod seulement quand la variable de dépôt `ANALYTICS_TOKEN` est définie.

## Mise en ligne

| Branche | Adresse | Workflow |
|---|---|---|
| `stage` | https://stage.frenchpouletclub.com (non indexé) | `.github/workflows/stage.yml` |
| `main` | domaine de prod (variable `PROD_DOMAIN`) | `.github/workflows/prod.yml` |

1. Travailler sur `stage`, pousser : le site de test se met à jour en ~1 min.
2. Valider : ouvrir une pull request `stage` → `main` et la fusionner. La prod se met à jour.

Le site de test est publié dans le dépôt `lucag322/french-poulet-club-stage` (ne rien y modifier à la main) grâce à la clé de déploiement `STAGE_DEPLOY_KEY`.

## DNS

- `stage` : enregistrement CNAME vers `lucag322.github.io`, puis définir la variable de dépôt `STAGE_DOMAIN=stage.frenchpouletclub.com`. Sans elle, le test est sur https://lucag322.github.io/french-poulet-club-stage/
- Prod (plus tard) : voir la doc GitHub Pages pour un domaine apex (4 enregistrements A + AAAA), puis définir la variable de dépôt `PROD_DOMAIN`.

## Licences

Police Unbounded : SIL Open Font License 1.1 (`fonts/OFL.txt`). Photos actuelles provisoires, à remplacer par le shooting du chef.
