# Recipedia

A map of 11,534 dishes from 66 cuisines, with recipes, cooks and cookbooks.
Live app: https://claude.ai/artifact/U9qbH6hrrkRWBcwQhThTRU

## Status (Nov 22 2026, app v21)

- 11,101 recipes. 9,250 of 11,534 dishes (80%) have at least one recipe.
- v21 added the wave 2 recipes (7,972, one per dish that had none) to docs/data.json. Nothing else in the app changed from v20.1.
- 2,284 dishes still have no recipe:
  - 588 are handed to ChatGPT (handoff/). When its CSV comes back, run `python3 pipeline/add_recipes.py that.csv`, check the summary, then publish docs/data.json.
  - About 1,690 were skipped because no trustworthy recipe turned up (data/wave2-skipped.tsv). Some Japanese, Chinese and Brazilian skips were too strict and are worth a second pass.

## Open decisions

- simplechinesefood.com (88 recipes) takes recipes from home cooks under usernames. They are in the app for now. Drop or keep.
- What next: techniques, a second pass on the skipped dishes, or historical recipes from vintage cookbooks (thefoodhistorian.com/vintage-cookbooks.html, mostly 1870s to 1920s American).
- Whether Start should be the default view, and when to bring back zoom, galaxy and globe (hidden since v20.1).

## Layout

| Path | What |
|---|---|
| docs/ | The published app: index.html, data.json, globe.json, d3.min.js |
| data/dishes.csv | All 11,534 dishes |
| data/recipes-original.csv | Recipes before wave 1 |
| data/wave2-recipes.csv | Wave 2 rows as merged (dish_id, cook, source, recipe_title, note, url) |
| data/wave2-skipped.tsv | Dishes skipped in wave 2, with reasons |
| data/import-fixes.tsv | Drops and cook corrections (already applied in v21) |
| pipeline/ | Worker brief and scripts used for wave 2, plus add_recipes.py for new CSVs |
| handoff/ | ChatGPT prompt and the 588 dishes given to it |

## data.json format

Keys: D dishes, Rc recipes, B cookbooks, P flavor profiles, X recipe comparisons, L dish links, F families, C cuisines, R regions, K courses, plus map geometry (Rg, KC, G).
A recipe row is `[dish_index, title, cook, source, url, note]`, where dish_index points into D.
Serialize with `json.dump(d, f, separators=(',', ':'), ensure_ascii=False)` to keep the same format.

## Picking up in a new chat

Read this README, then work in the repo. Commit each change with a clear message, so the history is the changelog.
