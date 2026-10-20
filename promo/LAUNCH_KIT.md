# Restaurant Radar — LAUNCH KIT (promo package)

Built 2026-10-17. Files on disk only: nothing committed, pushed or deployed. The owner deploys.

## 1. Package index

| Path (under `D:/Hermes_Core/workspace/Restaurant_Radar/promo/`) | What it is |
|---|---|
| `index.html` | Self-contained landing page: hero, 3 value props, video, pricing, FAQ, CTA band, footer. Zero external resource loads; CSP self + inline. |
| `assets/hero.jpg` | Hero image: the real product map screenshot (`assets/img/product-map.png`), JPEG-compressed for the web. |
| `assets/og.png` | 1200x630 Open Graph card ("Know what's open before you head out." + restaurantradar.app). |
| `assets/social_1080.png` | 1080x1080 square post (Founding Professional $9/mo, City License $199/mo). |
| `assets/scenes/s2_venues.png` … `s6_endcard.png` | 1280x720 PIL-drawn storyboard cards for the video. |
| `video/radar_16x9.jpg` | 1280x720 poster for the video element. |
| `video/BRIEF.md` | 6-scene storyboard, VO lines, recommended edge-tts voice. |
| `video/storyboard.json` | Machine storyboard for `Teams/Marketing/video/make_promo_video.py` (schema of `test_storyboards/wwe_test.json`; slug `radar`, 5 scenes + CTA `restaurantradar.app`). Dry-run validated 2026-10-17: `VALIDATION OK ... scenes=5 voice=en-US-AndrewNeural`. Render (owner/next step, NOT run): `python D:/Hermes_Core/Teams/Marketing/video/make_promo_video.py --storyboard D:/Hermes_Core/workspace/Restaurant_Radar/promo/video/storyboard.json --out D:/Hermes_Core/workspace/Restaurant_Radar/promo/video` |
| `video/radar_16x9.mp4` | NOT built yet. The page already points at this exact path; drop the render here. |
| `fonts/Inter-latin.woff2`, `fonts/JetBrainsMono-latin.woff2` + `OFL-*.txt` | Self-hosted OFL fonts with their licences. |
| `LAUNCH_KIT.md` | This file. |
| `_manifest.json` | Every file with byte counts measured by `wc -c`, plus the verified_against map. |

## 2. Deploy commands (inspected, NOT run)

Site repo: `D:/Hermes_Core/workspace/Restaurant_Radar`, branch `gh-pages`, remote
`origin https://github.com/jjordanjr74-dot/restaurantradar-site.git`, CNAME `restaurantradar.app`.
`git status --short` before this build showed only `?? promo/` (the new dir).

```bash
cd D:/Hermes_Core/workspace/Restaurant_Radar
python radar_site_premium_gate.py          # must print SUMMARY: 47/47 checks pass
git add promo/
git commit -m "promo: Restaurant Radar landing + social + video brief"
git push origin gh-pages
# after GitHub Pages rebuilds:
curl -s -o /dev/null -w "%{http_code}\n" https://restaurantradar.app/promo/
```

The page will serve at `https://restaurantradar.app/promo/`. It links up to `../pricing.html`,
`../city-license.html`, `../privacy.html` and `../assets/icon.svg`, which exist in the same repo.

Checkout buttons point at the app's checkout endpoints, not at a pasted Stripe session:
`https://app.restaurantradar.app/api/checkout/founding_professional` and `.../city_license`. Each GET
returned HTTP 303 to a fresh `checkout.stripe.com/.../cs_live_...` session, and that session URL returned
HTTP 200 (checked 2026-10-17). Reason: a Stripe Checkout session URL expires, so a `cs_live_` link
pasted into a static page stops working; the endpoint mints a new live session on every click.
Re-run the check before posting:

```bash
for t in founding_professional city_license; do
  u=$(curl -s -o /dev/null -m 25 -w '%{redirect_url}' https://app.restaurantradar.app/api/checkout/$t)
  echo "$t -> ${u:0:60}"; curl -s -o /dev/null -m 25 -w "%{http_code}\n" "$u"
done
```

## 3. Video placement guide (Shorts / Reels — road-trip angle)

- Hook in the first 2 seconds: scene 1 VO "Heading down I-25 hungry?" over the real map.
- YouTube Shorts and Instagram Reels: 9:16 crop of the 16:9 master, about 30 s, captions burned in.
- Facebook / landing page: the 16:9 master at `promo/video/radar_16x9.mp4`.
- Caption template: "Driving Colorado Springs to Pueblo? 932 places to eat and 40 fuel stops on one live map. Free, no account. restaurantradar.app"
- Hashtags: #Pueblo #ColoradoSprings #I25 #RoadTrip #FoodTruck #Colorado
- Link in bio / pinned comment: `https://restaurantradar.app/promo/` (after deploy) or `https://app.restaurantradar.app`.
- Suggested post times (a starting guess to test, not a measured result): Thursday–Saturday, late morning and late afternoon.

## 4. Two-week posting cadence

| Day | Channel | Asset | Message |
|---|---|---|---|
| 1 (Mon) | Facebook page + Pueblo groups (where allowed) | `assets/og.png` via link share | Launch: one live map, 932 venues, 8 cities |
| 2 (Tue) | Instagram feed | `assets/social_1080.png` | Venue owners: Founding Professional $9/mo |
| 3 (Wed) | Shorts + Reels | `video/radar_16x9.mp4` (once rendered) | Road-trip hook, I-25 |
| 5 (Fri) | Facebook / Instagram story | `assets/scenes/s3_cities.png` | 8 cities + 40 fuel stops |
| 6 (Sat) | Shorts + Reels | same video, new caption | "Open right now?" angle (scene 4) |
| 8 (Mon) | LinkedIn / email to chambers, BIDs, tourism offices | `assets/og.png` + City License page | City License $199/mo, white-label |
| 9 (Tue) | Instagram feed | `assets/scenes/s2_venues.png` | Food trucks: 366 on the map |
| 10 (Wed) | Shorts + Reels | video re-cut, scene 5 first | Venue-owner angle, $9/mo |
| 12 (Fri) | Facebook | `assets/scenes/s4_hours.png` | Why some pins say hours unknown (honesty post) |
| 13 (Sat) | Shorts + Reels | video, end-card first frame | "Check the radar first" |
| 14 (Sun) | Review | — | Count real clicks/checkouts from Stripe and the app; keep only what moved |

Customer-facing posts are a human gate: the owner publishes, the agent stages.

## 5. Staged vs live — truth table

| Item | State | Evidence |
|---|---|---|
| Live app `https://app.restaurantradar.app` | LIVE | `curl` HTTP 200, 2026-10-17 |
| Marketing site `https://restaurantradar.app/` | LIVE | `curl` HTTP 200, 2026-10-17 |
| Founding Professional checkout ($9/mo) | LIVE | endpoint 303 -> `cs_live_` session, session HTTP 200 |
| City License checkout ($199/mo) | LIVE | endpoint 303 -> `cs_live_` session, session HTTP 200 |
| `promo/index.html` + images | STAGED (on disk, not pushed) | `git status`: `?? promo/` |
| `promo/video/radar_16x9.mp4` | NOT BUILT | storyboard in `video/BRIEF.md`; poster exists |
| Social posts | STAGED | owner publishes |

### Claimable today (each traced to a source)
- 932 venues: 462 restaurants, 366 food trucks, 104 cafes — `restaurant_radar.db` table `restaurants`.
- 8 cities: Colorado Springs 700, Pueblo 188, Fountain 14, Pueblo West 12, Manitou Springs 8, Falcon 4, Peyton 4, Fort Carson 2 — same table.
- 40 fuel stops (Pueblo 38, Pueblo West 2) — table `gas_stations`.
- 404 venues with published hours (source OSM) — `restaurants.hours_today`.
- Data sources: 923 OpenStreetMap, 8 roaminghunger, 1 operator — `restaurants.source`.
- Free to search, no account, no ordering / no cut — the site's own `index.html` and `pricing.html`.
- Prices $9/mo and $199/mo — `offer_truth.json` `advertised_prices_usd` + `app.py` `PLACEMENT_TIERS`.

### NOT claimable yet (do not put in any post, caption, graphic or VO)
- **Verified stops / a verified badge.** `verified_at` is empty on all 932 venue rows and all 40 fuel rows. The vendor pack (`Teams/Marketing/04_RestaurantRadar_VENDOR_PACK.md`) marks this layer as a missing prerequisite.
- **Safety ratings, "safe to nap", lit parking, security.** `gas_station_reviews` has 0 rows; `restaurant_comments` has 0 rows.
- **Amenities (showers, restrooms, pet areas, truck parking) as a data layer.** Only 4 of 40 fuel rows carry an operator-entered amenities string; none is checked.
- **Reviews, star ratings, testimonials.** 0 review rows; `rating` is empty on all rows. The live site's index.html shows "3 reviews from early users" with two quoted travellers; the database and the live reviews API (`/api/gas-stations/1/reviews` -> `total_reviews: 0`) do not back them. Not reused here — see blockers.
- **Fuel prices.** `fuel_prices` has 0 rows.
- **Traffic, views, users, paying customers.** `listing_views` 0 rows, `placements` 0 rows.
- **"Phone and hours on every pin."** Phone is present on 495 of 932 venues, hours on 404.
- **"42 fuel stops"** (live site copy). The database holds 40.
- **"Fort Spring area"** (live site copy). The database city is Fort Carson.
- **Verified tier (~$25/mo) and Featured tier (~$60/mo)** — `offer_truth.json` marks both "not yet sellable". The Professional and Premier tiers listed as planned on `pricing.html` have no live checkout. None of these appear in the promo.
