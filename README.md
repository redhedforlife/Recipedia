# Recipedia

A map of 11,534 dishes from 66 cuisines, with recipes, cooks and cookbooks.
Live app: https://claude.ai/artifact/U9qbH6hrrkRWBcwQhThTRU

## Status (Nov 22 2026, app v21)

- 11,013 recipes. 9,162 of 11,534 dishes (79%) have at least one recipe.
- v21 added the wave 2 recipes (7,972, one per dish that had none) to docs/data.json. Nothing else in the app changed from v20.1.
- 2,372 dishes still have no recipe:
  - 588 are handed to ChatGPT (handoff/). When its CSV comes back, run `python3 pipeline/add_recipes.py that.csv`, check the summary, then publish docs/data.json.
  - About 1,690 were skipped because no trustworthy recipe turned up (data/wave2-skipped.tsv). Some Japanese, Chinese and Brazilian skips were too strict and are worth a second pass.

## Open decisions

- Live at https://tryrecipedia.com (GitHub Pages, main branch, /docs folder; docs/CNAME holds the domain, registered at Namecheap). redhedforlife.github.io/Recipedia redirects there. og:image points at https://tryrecipedia.com/preview.png.
- Visitor stats: none yet (GoatCounter is a free option).

- What next: techniques, a second pass on the skipped dishes, or historical recipes from vintage cookbooks (thefoodhistorian.com/vintage-cookbooks.html, mostly 1870s to 1920s American).
- A plate laid out by dish type (a second tiling, families first). Not built: the script that made the plate's weighted-Voronoi layout was lost on Nov 2, so it would need a new tiler. v23 covers the browsing side with lenses instead.
- Whether Start should be the default view, and when to bring back zoom, galaxy and globe (hidden since v20.1).

## Layout

| Path | What |
|---|---|
| docs/ | The published app: index.html, data.json, globe.json, d3.min.js, preview.png (link preview) |
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

## UAT (test site)

- https://tryrecipedia.com/uat/ is the test copy, from docs/uat/. Changes go there first; prod (docs/index.html) only changes once they're approved.
- The UAT page is the same file as prod. It sees /uat/ in its address and then turns off PostHog, adds noindex and shows a "UAT build, not live" badge. docs/robots.txt also blocks /uat/.
- Promote to prod: `cp docs/uat/index.html docs/index.html` (plus any data file that changed in docs/uat/), commit, push.
- UAT forms still send tweaks and recipe links to the real Supabase review queue. Reject test entries in review.html.

## Picking up in a new chat

Read this README, then work in the repo. Commit each change with a clear message, so the history is the changelog.

## Changelog

- Nov 28 2026: v34 to v37 released to prod. docs/index.html now matches docs/uat/index.html.
- v37 (Nov 27 2026, UAT only): calmer dish panel and phone screen. Each recipe is one row: cook, time and the one thing that sets it apart; the whole row opens the recipe. The comparison table sits behind "Compare side by side". Add a recipe link, Add your own tweak and the recipe-search sites are quiet text links. Phones: the toolbar steps aside once you are inside the plate (a Filter chip stays when a filter is on); search is an icon that opens the field; the view button is icon-only.
- v36 (Nov 27 2026, UAT only at /uat/): recipe tiles. Choosing a recipe tile on the plate shows an "Open on {site}" pill under it, and a second tap on the same tile opens the recipe in a new tab (event Clicked out, via: tile). The flat plate can no longer be dragged away: the middle of the view always stays over the plate (zoom.constrain). PostHog host is now one setting, PH_PROXY, ready for the managed proxy at r.tryrecipedia.com once it is live (empty = direct).
- v35 (Nov 26 2026, UAT only at /uat/, not yet in prod): zoom coach. On the first two visits a small animation in the middle of the plate shows how to zoom (a scroll wheel on desktop, a pinch on touch screens, with "or click/tap a cuisine"); it leaves on the first interaction or after 8 seconds. Event: Saw zoom hint. Heatmap rebuilt from Nov 24 to 26 outside visits; heat/build.py also reads a compact L/T/O export.
- v34 (Nov 26 2026, UAT only at /uat/, not yet in prod): fixes from the design critique. One-line promise under the wordmark; Start from dishes you cook (was Pick 3 favorites) and Surprise me as the main buttons; Surprise me works in one click, with an arrow for courses; About as quiet text and in the View menu. Phone: map fits above the real toolbar, one-row toolbar, 44px targets, an empty kitchen opens the sheet tall. Keyboard: focus rings on filter and Surprise items, focus returns on close, arrow keys in the Surprise menu, search is a combobox, map after the header in tab order. Search: no "No exact match" above exact matches, full names for repeated categories, a "Filter by" row for ingredient words. Plate key (has a recipe, more dishes inside, size); About explains the plate; no bare popularity number. Errors in plain words with a retry; a failed recipe-link send no longer reloads; one document head; 3:1 control borders.
- v33 (Nov 24 2026): Tweaks. docs/tweaks.json holds three suggested tweaks for the 150 most popular dishes (source: data/tweaks-top150.txt). Visitors can add their own tweak or a recipe link; both go to Supabase (project recipedia, vfitqbrwpnwwlmhxhbox) as pending and show on the dish only once approved. Review page: tryrecipedia.com/review.html (admin sign-in; admins listed in public.admins). Row level security: anyone can insert pending rows, only approved rows are readable, only admins can change status; a trigger caps sends at 60 per 10 minutes.
- v32 (Nov 24 2026): No meat now means no meat or fish in the dish's proteins. Filtering lights the plate without opening the panel; the filter's List button opens it. Cookbook recommendations removed from every panel, the browse header and search (the data and #b- links still work).
- v31 (Nov 24 2026): Filter (ingredients by group, plus difficulty; every pick narrows, options show what's left; lens type 'filter', hash #x-key+key), Surprise me (random dish with recipes by course, from the filter when one is on), Pick 3 favorites (front door to Your kitchen). Events: Opened filter, Filtered, Surprise me, Tapped Pick 3 favorites.
- v30 (Nov 24 2026): private heatmap. docs/index.html draws a heat overlay only when window.HEAT_MODE is set and heat.json loads (never on the public site). heat/build.py turns a PostHog export of Looked at, Tapped plate and Opened dish/recipe rows into heat/out/ (a copy of the site plus heat.json), published as the private claude.ai artifact "Recipedia heatmap". Raw rows stay out of git.
- v29 (Nov 24 2026): heatmap data. PostHog heatmaps on (page clicks, rage clicks, scroll). Plate events in plate coordinates (x, y from -1 to 1, zoom 1 = whole plate): Tapped plate (what was hit) and Looked at (a view held 1.5 s or more, with seconds, cuisine, dish, whether the panel was open).
- v28 (Nov 24 2026): PostHog usage tracking on tryrecipedia.com only (US project, session replay with the canvas at 2 fps). Named events: Opened dish/recipe/cuisine/group/list (with how: pick or zoom), Whole plate, Searched, Clicked out (recipe, wikipedia, book, recipe search), Tapped About, Opened browse, Switched view, Closed panel, Expanded list, Tapped I cook this. About text says visits are recorded anonymously.
- v27 (Nov 23 2026): an About button replaces the Has recipes filter and opens the panel with the about text first. CSV exports are out of the View menu (the code stays). Menu reworded: Your kitchen (find your next dish, from what you cook today), The whole plate (explore the world's cuisines), Browse.
- v26 (Nov 23 2026): the panel opens only when you pick something: tap a dish or recipe, choose a search result, or open a link to a dish. Zooming, and tapping a cuisine or family, keeps the plate clear. Tapping the dish the zoom has settled on opens it.
- v25 (Nov 23 2026): search groups results: matching categories in bold with their dishes indented under them (Burgers, then Burger, Cheeseburger...), and a sub-group no longer matches on its family's name alone. Dish panel reordered and folded: recipes, then More X from Y and Related dishes (three each, then a quiet "… N more" row), cookbooks two then more; lens lists show ten then more. On desktop the search sits atop the open panel and floats in the header when the panel is closed.
- v24 (Nov 23 2026): the plate opens alone. Search floats in the header; the panel slides in when something is picked (bottom sheet at half height on phones) and closes with its X. The home panel (dish types, websites, cuisines, About) moved to View > Browse and about. Removed the Area = popularity and More dishes keys.
- v23 (Nov 23 2026): browse by dish type and by website. Home panel lists the 42 dish types and the top recipe websites. A dish type opens lit across the plate with a By cuisine list (Sandwiches, then American, then every American sandwich). Each website has its own lens (#w-host), and a recipe's source links to it.
- v22 (Nov 23 2026): public-release cleanup. Page title, description, link preview and icon; About note on the home panel; dropped 88 Simple Chinese Food recipes (user-submitted); one site name per website; 104 cook first names filled in, 56 usernames replaced by the site name; CSV export works outside Claude.
- v21 (Nov 22 2026): wave 2 recipes added (7,972).
