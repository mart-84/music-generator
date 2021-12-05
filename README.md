# music-generator

Quelques classes pour transformer les fichiers de musique midi en fichiers texte, analyser la fréquence des notes et générer une nouvelle musique basée sur ces statistiques.

La génération de musique se découpe en plusieurs étapes :
- Transformation des fichiers midi en fichiers csv
- Transformation des fichiers csv en fichiers txt
- Analyse de la fréquence d'enchainement des notes
- Génération de la musique
- Transformation du nouveau fichier txt en csv, puis midi


## Transformation midi/csv
Les scripts utilisent la librairie python `mido` afin d'utiliser les fichiers midi sous forme d'objet.

Les fichiers csv générés ont la forme suivante :

```CSV
"note_on","63","1","0"
"note_off","63","1","200"
"note_on","62","1","0"
"note_off","62","1","300"
```

Chaque ligne comporte 4 champs distincts. Le premier champ correspond à un début/fin de note, le deuxième champ correspond à la note entre 0 et 127, le troisième champ correspond au channel (il est inutilisé pour la génération), le quatrième et dernier champ correspond au temps en ticks midi après lequel la ligne prend place.

Dans notre exemple, on obtiendra la note 63 qui joue pendant 200 ticks, immédiatement suivie par la note 62 durant 300 ticks.


## Transformation csv/txt
Les fichiers txt sont les fichiers utilisés par l'algorithme d'analyse des fréquences. Ils regroupent sous forme de *mots* les différentes notes jouées à un instant t. Les mots sont séparés par des espaces. Un mot de n caractères représente les n notes jouées pendant une durée donnée. Un mot peut avoir une longueur nulle si aucune note n'est jouée pendant un certain intervalle de temps. La durée est configurable lors de la création des objets. 

Le changement de la durée donne plus ou moins de possibilité lors de la génération d'avoir des notes très courtes, mais change aussi la précision de l'analyse. La durée par défaut est de 50 ticks.



## Analyse des fréquences
L'algorithme d'analyse utilise les musiques au format txt pour faire des statistiques sur les enchainements de notes. En fonction des n dernières notes, il mémorise quelle est la note suivante, et à quelle fréquence cette note apparait. Par exemple, si on analyse sur les 2 dernières notes, et que l'on a les notes do et si, l'algorithme trouvera que la note suivante est un si dans 14 cas et un la dans 3 cas. Il stocke ce résultat dans un dictionnaire, exportable au format json.

Voici un exemple de dictionnaire pour deux premières notes connues :
```JSON
{
    "] ]": {
        "]": 311,
        "": 25,
        "\\": 2,
        "]`d": 2,
        "]bg": 1,
        "Q]": 1
    }
}
```


## Génération de la musique
La génération de la musique se base sur le dictionnaire créé par l'algorithme précédent, et exploite les statistiques pour donner la probabilité de la prochaine note, en connaissant les précédentes.
L'algorithme crée autant de notes que souhaité. A titre d'exemple, avec les paramètres par défaut d'analyse sur 50 ticks, 10000 notes représentent environ 8'40'' de musique

La musique créée est au format txt, prête à être retransformée en csv puis midi.
