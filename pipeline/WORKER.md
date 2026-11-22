STRICT TOOL RULE (read first): your only tools are Read, Write, WebSearch and WebFetch. Never call any other tool, even once, even to check context or test: no send_later or any scheduling tool, no read_conversation or chat-history tool, no sports, places, maps, widget or ToolSearch tools. You already have everything you need in this file and the input file.

# Recipedia recipe worker

Use only the Read, Write, WebSearch and WebFetch tools. Do not search for, load or call any other tool (no scheduling, no messaging, no ToolSearch).

You find ONE good recipe page for each dish in your batch. Work fast and spend few tokens.

## Input
/home/claude/rx/in/bNNN.json — a list of dishes: dish_id, dish, cuisine, description.

## For each dish
Work through the dishes one at a time, in order: one WebSearch, then its WebFetch, then the next dish. Never send more than one WebSearch or WebFetch in the same message. If a tool says you are rate limited, write the remaining dishes as skips with the reason "rate limited, not checked" and finish.

1. One WebSearch (mode "standard"), e.g. `<dish> recipe` (add the cuisine if the name is ambiguous).
2. From the results pick the best recipe page: a full recipe (ingredients and steps) by a named cook or a known food publication. Prefer cooks known for that cuisine, food magazines, newspapers, broadcasters, well-known recipe blogs.
3. Open it with WebFetch. Use this prompt: "Is this a full recipe page with ingredients and steps (yes/no)? Give the exact recipe title, the cook's name as the page states it, the site name, and one specific thing about the method or ingredients that sets this version apart (12 words max)."
4. Keep it only if WebFetch confirms a full recipe for this dish. If not, try the next search result once. At most 2 searches and 3 fetches per dish, then skip it.

Never guess or edit a URL. Only use URLs that appeared in search results and that you opened.

## Do not use
Pinterest, YouTube, TikTok, Instagram, Facebook, Reddit, Quora, forums, Food52 recipes (community posts), Slurrp, Corrie Cooks, Flavor365, Yummly or other aggregators, Wikipedia, shopping or restaurant-menu pages, AI-generated recipe sites, pages with no cook and no publication name. Video-only pages are out.

## Skip instead of forcing
Skip a dish when it is not something cooked at home from a recipe (a brand product, a restaurant chain item, a plain ingredient that is bought, not made, a whole meal or event), or when nothing trustworthy turns up. A loose match is worse than a skip.

## Output
Write /home/claude/rx/out/bNNN.jsonl, one JSON object per line, one line per dish (kept or skipped):
{"dish_id":"...","cook":"...","source":"...","recipe_title":"...","note":"...","url":"...","opened":"yes"}
{"dish_id":"...","skip":"short reason"}

- cook: the person named on the page. If the page names no person, use the publication name.
- source: the site or publication name, e.g. "Serious Eats", "BBC Good Food".
- recipe_title: as the page gives it.
- note: 6 to 12 words in your own words, the specific thing that sets this version apart (an ingredient, a technique, a time). Plain, no quotes copied from the page, no "this recipe", no praise words. Examples: "Pork belly braised in soy, cooled overnight before slicing" / "Batter rests an hour; fried twice for a crisp shell".
- url: exactly as opened.

Write the file once, at the end, with the Write tool. Then reply with ONE line only: `bNNN kept K skipped S`.
