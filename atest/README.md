# Tests d'acceptation

## Vérification des liens

Après chaque déploiement, la CI lance un parcours complet avec linkchecker, liens externes compris.

Pour le rejouer en local, depuis `atest/`, le site étant servi par `npm run dev` :

```sh
pip install -r requirements.txt
linkchecker --config=linkcheckerrc http://localhost:4321/
```

Les exceptions sont dans `linkcheckerrc` : `ignore` pour les liens qui ne répondent plus (site fermé), `ignoreerrors`
pour les hébergeurs qui bloquent les robots (le lien est valide mais répond une erreur hors navigateur).

## Vérification de la pertinence des ressources

Chaque ressource est évaluée pour sa pertinence en rapport avec sa présence dans le site.

Un agent IA est utilisé pour vérifier cette pertinence : ressource en français, parle de test ou de qualité, activité, 
catégorie, etc.

Robot Framework est utilisé pour lancer les tests. Il alimente le prompt de l'agent IA, lance son exécution et vérifie 
son verdict en retour via des assertions.

Pour lancer les tests, il suffit de lancer la commande Robot Framework suivante :

```shell

robot --prerunmodifier atest/libs/TestCaseGenerator.py --variable AGENT_ID:ag_123456789 atest/tests/relevance.robot
```

En plus de la clé d'API (variable d'environnement `AGENT_API_KEY`), préciser l'agent à utiliser (`AGENT_ID`).

# Qualité du code de test

Le code Python et Robot Framework de ce répertoire est vérifié à chaque pull request. Les outils sont configurés dans
`pyproject.toml` et se lancent **depuis `atest/`**, avec le `Makefile` : ruff et robocop cherchent leur configuration à
partir du répertoire courant, et l'ignorent silencieusement si on les lance d'ailleurs.

```sh
make install         # installe les outils (requirements-dev.txt)
make                 # formate puis analyse tout
```

Une cible par outil, à restreindre au besoin avec `file=` (`make lint file=libs`) :

| Cible                 | Outil                                                   |
|-----------------------|---------------------------------------------------------|
| `make format`         | `ruff format`                                           |
| `make lint`           | `ruff check --fix`                                      |
| `make docstrfmt`      | `docstrfmt` (formatage des docstrings reStructuredText) |
| `make sphinxlint`     | `sphinx-lint`                                           |
| `make robocop-format` | `robocop format`                                        |
| `make robocop-lint`   | `robocop check`                                         |

La CI lance les mêmes outils en mode vérification (`--check`) : ils échouent au lieu de corriger.

Passer par le `Makefile` évite deux pièges de docstrfmt : sa recherche de configuration s'ancre sur le répertoire `.git`
(d'où `--pyproject-config`) et son cache ne tient pas compte de la configuration (d'où `--ignore-cache`).
