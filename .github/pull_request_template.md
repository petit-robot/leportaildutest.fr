## Nature de la contribution

- [ ] Ajout d'une ou plusieurs ressources
- [ ] Modification d'une fiche existante
- [ ] Autre (site, documentation, tests…)

## Ressource(s) concernée(s)

<!-- Nom de la ressource et chemin du fichier, ex. content/directory/blogs/le-blog-du-testeur.md -->

## Description

<!-- Que fait cette PR ? Pour une modification, précisez la valeur avant/après. -->

## Vérifications

- [ ] La ressource est francophone et porte sur le test ou la qualité logiciels
- [ ] Le fichier est dans `content/directory/<catégorie>/` et son nom sert de slug
- [ ] Les champs obligatoires sont renseignés : `title`, `tags`, `description`, `link`
- [ ] Les `tags` correspondent à des clés définies dans `site/src/config/settings.toml`
- [ ] L'image éventuelle est dans `content/images/<slug>.png` et référencée par `image: "../../images/<slug>.png"`
- [ ] `npm run build` passe dans `site/`
