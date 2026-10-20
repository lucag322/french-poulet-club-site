# French Poulet Club — site

Site vitrine du French Poulet Club (Stockholm, ouverture printemps 2028). Une seule page statique, sans build : `index.html`, `img/`, `fonts/`.

## Aperçu local

```bash
python3 -m http.server 8766
```

## Mise en ligne

| Branche | Adresse | Workflow |
|---|---|---|
| `stage` | https://stage.frenchpouletclub.com (non indexé) | `.github/workflows/stage.yml` |
| `main` | domaine de prod (variable `PROD_DOMAIN`) | `.github/workflows/prod.yml` |

1. Travailler sur `stage`, pousser : le site de test se met à jour en ~1 min.
2. Valider : ouvrir une pull request `stage` → `main` et la fusionner. La prod se met à jour.

Le site de test est publié dans le dépôt `lucag322/french-poulet-club-stage` (ne rien y modifier à la main) grâce à la clé de déploiement `STAGE_DEPLOY_KEY`.

## DNS

- `stage` : enregistrement CNAME vers `lucag322.github.io`
- Prod (plus tard) : voir la doc GitHub Pages pour un domaine apex (4 enregistrements A + AAAA), puis définir la variable de dépôt `PROD_DOMAIN`.

## Licences

Police Unbounded : SIL Open Font License 1.1 (`fonts/OFL.txt`). Photos actuelles provisoires, à remplacer par le shooting du chef.
