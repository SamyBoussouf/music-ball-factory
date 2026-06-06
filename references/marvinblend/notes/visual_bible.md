# Visual Bible — marvinblend style
*Extracted from refs 001–006 | 2026-06-06*

---

## La structure fondamentale

Chaque vidéo est une **playlist musicale** sur un parcours unique descendant.
La bille part en haut, la caméra la suit jusqu'en bas. Le parcours est infini (loop).
Chaque section du parcours = 1 chanson = 1 type d'instrument = 1 ambiance visuelle.

**Ce n'est pas juste "instruments différents" — c'est des MONDES différents.**
(ref_004 Mario World : tout change, le décor, les couleurs, les objets)

---

## Les 3 formats vidéo identifiés

| Format | Texte | Exemple |
|---|---|---|
| **Playlist numérotée** | `1. Song Name` / `2. Song Name` | ref_001, 003, 004, 005, 006 |
| **POV/Hook viral** | Phrase émotionnelle plein écran | ref_002 ("POV: the song that's STILL peak 2 years later") |
| **Single song** | Titre seul | sous-format possible |

**Format à implémenter en priorité : Playlist numérotée.**
Le texte n'a PAS toujours de box fond gris. ref_005/006 = texte blanc pur, gras, sans fond.
ref_001/002/003 = texte blanc avec rectangle arrondi semi-transparent derrière.

---

## Les palettes d'ambiance (le décor adapte la musique)

| Palette | Couleur mur | Usage | Refs |
|---|---|---|---|
| **Warm beige** | `#D4C2B8` (0.83, 0.76, 0.72) | Dreamcore, nostalgie, pop calme | 001, 002, 006 |
| **Cool grey** | `#C8C8C8` (0.78, 0.78, 0.80) | Classical, éthéré, instruments acoustiques | 005, 006 |
| **Slate blue** | `#8A9AAB` (0.54, 0.60, 0.67) | Trap, hip-hop, dark vibes | 003 |
| **Pure white** | `#F0F0F0` (0.94, 0.94, 0.94) | Épuré, minimal | 004 section vibraphone |
| **Themed world** | N/A — full environment | Quand la musique a un univers fort (Mario, etc.) | 004 |

**Règle** : la palette se choisit en fonction du genre musical, pas aléatoirement.

---

## Les instruments — catalogue complet

Chaque instrument est une SCULPTURE 3D qui ressemble à l'instrument réel.

| Nom | Forme 3D | Matériau | Couleur | Taille relative | Réf |
|---|---|---|---|---|---|
| Steel Pan | Disque plat | Bois/bambou | `#B88030` warm brown | ø0.12 | 001, 006 |
| Xylophone bar | Rectangle arrondi | Bois | Natural brown ou **jaune vif** `#E8D800` | 0.14×0.035 | 001, 006 |
| Xylimba bar | Rectangle arrondi | Bois bronze | `#C07830` copper | 0.12×0.03 | 005 |
| Crystallophone | Tube cylindrique transparent | Verre/cristal | Transparent + reflets | ø0.015 L0.10 | 005, 006 |
| Glass sphere | Sphère pleine | Verre | Transparent irisé | ø0.03 | 006 |
| Handbell | Forme cloche | Métal coloré | Rose, violet, bleu, vert | h0.06 | 005 |
| Heart bell | Forme cœur | Métal coloré | Rose, violet, vert | 0.05 | 005 |
| Flute/Recorder | Cylindre avec embout | Céramique blanc | Blanc mat | L0.18 ø0.02 | 005 |
| Vibraphone bar | Grand rectangle | Métal gris | `#8090A0` steel blue | 0.18×0.04 | 004 |
| Boomwhacker | Grand tube PVC | Plastique mat | **Bleu**, **teal**, rouge... | ø0.025 L0.25 | 004 |
| 8-bit block | Cube pixelisé | Emission rouge | `#FF2020` + texture pixel | 0.05 cube | 004 |
| Chain bar | Rectangle petit | Métal doré/argent | Or `#C8A020` / argent | 0.06×0.018 | 001 |

---

## La bille — matériau & variantes

**Constante** : bille en verre avec motif swirl intérieur coloré. IOR ≈ 1.52.
Jamais une bille opaque. Toujours transparente avec couleur interne.

| Couleur swirl | Usage (humeur) | Refs |
|---|---|---|
| Bleu/teal + blanc | Calme, dreamcore | 001, 006 |
| Violet/magenta + blanc | Nostalgie, émotionnel | 002, 005 |
| Vert + blanc | Sections dark/trap | 003 |
| Rose/multicolor | Sections pop légères | 004 |

**Nombre de billes** :
- 1 bille = tempo modéré (< 140 BPM)
- 2 billes = tempo rapide, notes en rafale
- 3 billes = très rapide ou mélodie complexe à plusieurs voix

---

## L'impact visuel — la mécanique clé

**Quand la bille touche un instrument, il se passe quelque chose de visible.**

| Effet | Description | Quand |
|---|---|---|
| **Squash/stretch** | L'instrument se comprime légèrement et rebondit | Toujours |
| **Glow émissif** | L'instrument émet de la lumière au contact | Sections dark (ref_003) |
| **Lueur colorée** | Point light coloré suit la bille, teinte le sol | Sections dramatiques (ref_001 section 4) |
| **Light instrument** | Instrument blanc/clair qui brille au hit | ref_003 floating style |

**IMPLÉMENTATION BLENDER** :
- Squash : scale keyframe sur 3 frames (–1, 0, +2)
- Glow : material emission strength 0 → 8 → 0 sur 4 frames
- Point light : parented à la bille, intensity 0 → 20 → 0 sur hit

---

## Les rails — géométries par style

| Style rails | Forme | Sections | Attachement |
|---|---|---|---|
| Arc concave | Courbe douce en U | Steel pan, xylophone | Mur via pins chrome |
| Plateforme grille | Rectangle avec barreaux | Xylophone long, Hide dark fantasy | Mur |
| Chaîne segments | Horizontaux connectés | Confort chain | Mur |
| Suspendu | Aucun rail — fils | Floating style (ref_003) | Fil depuis haut |
| Staircase | Marches descendantes | Harpsichord | Mur, top-down |

**Tube radius rail** : 0.006 blender units
**End ball radius** : 0.015 blender units
**Chrome** : metallic 1.0, roughness 0.04, color [0.85, 0.87, 0.90]

---

## Caméra — comportement invariant sur toutes les refs

- **Lens** : 85mm (full frame equiv)
- **Dutch tilt** : 4–8° sur Z — jamais parfaitement droit
- **Angle mural** : oblique, jamais perpendiculaire au mur
- **DoF** : focus sur la bille, f/4, instruments lointains flous
- **Motion** : suit la bille avec damping (léger retard), smooth
- **Travelling** : direction diagonale (top-right → bottom-left en perspective caméra)
- **Distance mur** : 1.0–1.8 blender units selon section

---

## Lumière — setup de base

```
Lumière principale : Area light, warm [1.0, 0.92, 0.80], droite/haut, shadows on
Ambiance : World shader faible, couleur de la palette
Lumière accent : optionnelle, colorée, suit la bille en sections dark
```

Pour les sections cool grey / slate blue : remplacer par lumière froide [0.88, 0.93, 1.0].

---

## Texte overlay — 2 styles

**Style A — avec fond box** (ref_001, 002, 003) :
- Container : `rgba(30, 25, 20, 0.70)` arrondi
- Font : Inter Bold ou Poppins Bold
- Couleur texte : blanc #FFFFFF
- Position : top-left, margin 6% h, 8% v

**Style B — sans fond** (ref_005, 006) :
- Font : bold blanc pur
- Légère ombre douce (opacity 0.4)
- Position : top-center ou top-left

**Format du texte** : `[N]. Nom de la chanson`

---

## Le décor "real room" (ref_002)

Un style spécifique : la scène se passe dans une vraie pièce.
Fenêtre visible, lumière naturelle, rambarde d'escalier.
Les rails et instruments sont placés dans l'espace réel de la pièce.
Effet : "ce qui se passe dans l'appartement" → plus immersif, plus intime.
Ce style est une VARIANTE du style standard, pas le style par défaut.

---

## La règle d'or

> **L'instrument ressemble toujours à ce qu'il joue.**
> **La couleur/ambiance correspond au genre musical.**
> **La bille déclenche toujours une réaction visuelle au contact.**
> **La caméra suit la bille — jamais fixe.**
