# Le Portail du test logiciel

Le portail des ressources francophones du test logiciel : blogs, podcasts, newsletters, magazines, communautés, événements, emploi, formations et études.

👉 https://le-portail-du-test.fr

## Architecture

```
.
├── content/   # Le contenu du site (indépendant du thème)
│   ├── directory/   # L'annuaire : un fichier .md par ressource, rangé par sous-dossier de catégorie (blogs/, podcasts/…)
│   ├── blog/        # Articles de blog
│   ├── pages/       # Pages statiques (une route par fichier)
│   └── images/      # Images utilisées par le contenu
└── site/      # Le site Astro (thème Minted Directory)
    ├── src/             # Composants, layouts, config du thème
    ├── public/          # Fichiers statiques (favicon…)
    └── astro.config.mjs
```

Tout ce qui concerne Astro et le thème est isolé dans `site/` ; le thème charge le contenu depuis `../content` (voir `site/src/content.config.ts`).

## Développement

```sh
cd site
npm install
npm run dev      # serveur de développement
npm run build    # build statique dans site/dist/
```

La configuration du site (titre, navigation, source de l'annuaire…) se fait dans `site/src/config/settings.toml`.

Voir `site/README.md` pour la documentation du thème d'origine.
