# Le Portail du Test Logiciel

Le portail des ressources francophones du Test logiciel : blogs, podcasts, newsletters, magazines, communautés, événements, emploi, formations et études.

👉 https://leportaildutest.fr

## Contribuer

Les contributions sont les bienvenues : ajout d'une ressource manquante, correction ou mise à jour d'une fiche existante. Deux manières de participer, au choix.

### Par issue (aucune compétence technique requise)

- 👉 [Proposer une nouvelle ressource](https://github.com/petit-robot/leportaildutest.fr/issues/new?template=ressource-ajout.yml) : un formulaire guidé reprend les champs de la fiche (nom, lien, catégories, description…).
- 👉 [Proposer une modification](https://github.com/petit-robot/leportaildutest.fr/issues/new?template=ressource-modification.yml) : indiquez la fiche concernée et ce qu'il faut corriger.

### Par pull request

1. Forkez le dépôt et créez une branche.
2. Ajoutez un fichier ressource `.md` dans `content/directory/<catégorie>/` (le nom du fichier sert de slug), et l'image associée dans `content/images/`.
3. Ouvrez une pull request.

**Exemple d'un fichier ressource .md** :

Le fichier serait dans `content/directory/blogs/le-blog-du-testeur.md`.

Le contenu serait :

```yaml
---
title: "Le Blog du Testeur"
tags: ["blogs", "communautes"]
description: "Un blog francophone consacré au test logiciel : méthodologie, automatisation, métier et retours d'expérience."
link: "https://le-blog-du-testeur.example.com"
image: "../../images/le-blog-du-testeur.png"
paid: true
status: closed
---
```

### Différents champs possibles dans la ressource

| Champ | Obligatoire | Description |
| --- |-------------| --- |
| `title` | oui         | Nom de la ressource |
| `tags` | oui         | Une ou plusieurs clés de catégorie définies dans `site/src/config/settings.toml` (`blogs`, `communautes`, `emploi`, `etudes-formations`, `evenements`, `livres`, `magazines`, `newsletters`, `podcasts`) |
| `description` | oui         | Quelques phrases présentant la ressource |
| `link` | oui         | URL de la ressource |
| `image` | non         | Chemin relatif vers l'image, `../../images/<slug>.png` |
| `paid` | non         | `true` si la ressource n'est accessible qu'après paiement. Les livres ne sont pas concernés : ils sont payants par défaut. Les formations et abonnements payants (hors livres et conférences) ne sont référencés que dans le cadre d'un contrat d'affiliation : écrire à contact@leportaildutest.fr avant tout ajout (voir les [mentions légales](https://leportaildutest.fr/legal/mentions)) |
| `affiliate` | non         | `true` si la fiche fait l'objet d'un contrat d'affiliation. Affiche le badge « Affiliation » sur la carte et sur la fiche, comme l'exigent les [mentions légales](https://leportaildutest.fr/legal/mentions). N'a aucun effet sur le classement |
| `status` | non         | Actif par défaut (champ à omettre). `inactive` : plus aucune mise à jour depuis plus de 2 ans. `closed` : la ressource n'est plus directement disponible, ou le site annonce explicitement son arrêt — si son lien cesse de répondre, l'ajouter à `ignore` dans `atest/linkcheckerrc` |


## Architecture

```
.
├── content/   # Le contenu du site (indépendant du thème)
│   ├── directory/   # L'annuaire : un fichier .md par ressource, rangé par sous-dossier de catégorie (blogs/, podcasts/…)
│   ├── blog/        # Articles de blog (non utilisé actuellement)
│   ├── pages/       # Pages statiques (une route par fichier)
│   └── images/      # Images utilisées par le contenu
├── atest/     # Tests d'acceptation
└── site/      # Le site Astro (thème Minted Directory)
    ├── src/             # Composants, layouts, config du thème
    ├── public/          # Fichiers statiques (favicon…)
    └── astro.config.mjs
```

Tout ce qui concerne Astro et le thème est isolé dans `site/`.
Le thème charge le contenu depuis `../content` (voir `site/src/content.config.ts`).

## Développement

```sh
cd site
npm install
npm run dev      # serveur de développement
npm run build    # build statique dans site/dist/
```

La configuration du site (titre, navigation, source de l'annuaire…) se fait dans `site/src/config/settings.toml`.

Voir `site/README.md` pour la documentation du thème d'origine.

### Tests

Après chaque déploiement, la CI lance un parcours complet avec linkchecker, liens externes compris.

Pour le rejouer en local :

```sh
pip install -r atest/requirements.txt
linkchecker --config=atest/linkcheckerrc http://localhost:4321/
```
Les exceptions sont dans `atest/linkcheckerrc` : `ignore` pour les liens qui ne répondent plus (site fermé), `ignoreerrors` pour les hébergeurs qui bloquent les robots (le lien est valide mais répond une erreur hors navigateur).

## Licence

Voir [LICENSE.md](LICENSE.md).
