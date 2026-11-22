I'm attaching a CSV of 588 dishes (columns: dish_id, dish, cuisine, description). For each dish, find one real, published recipe on the web and give it back to me as a CSV.

Rules:
- One recipe per dish. It must be the dish described (right cuisine, right preparation), not a loose cousin.
- Open every page before you list it. Only give a URL you actually loaded, copied exactly. Never build or guess a URL.
- The page must be a full recipe with an ingredient list and steps. Not a menu, product page, encyclopedia entry, video with no written recipe, or news story about the dish.
- Prefer a named cook or a real publication (food magazines, newspapers, well-known cooks, established recipe blogs). Avoid AI content farms and recipe aggregators that copy other sites.
- If you can't find a trustworthy recipe after two searches, skip the dish. A skip is better than a weak match.
- Work through the list in chunks of about 50 dishes. After each chunk, give me the CSV rows for that chunk, then keep going until the list is done.

Output: CSV with exactly these columns, one row per dish, quoting any field that has a comma:

dish_id,cook,source,recipe_title,note,url

- dish_id: copied exactly from my file
- cook: the person named on the page; if none, the publication name
- source: the site or publication name
- recipe_title: the recipe's title as the page gives it
- note: one short line on what makes this version distinctive (an ingredient or method choice), in your own words
- url: the exact page you opened

For skipped dishes, add a row with the dish_id, leave cook, source, recipe_title and url empty, and put the reason in note.
