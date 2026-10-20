# Restaurant Radar — promo video storyboard (16:9 master, 9:16 crop for Shorts/Reels)

Output file (lands later, exact path the landing page already references):
`D:/Hermes_Core/workspace/Restaurant_Radar/promo/video/radar_16x9.mp4` — poster already built:
`D:/Hermes_Core/workspace/Restaurant_Radar/promo/video/radar_16x9.jpg` (1280x720).

Fact sources for every number below (read-only queries, 2026-10-17):
`D:/Hermes_Core/Monetization/Restaurant_Radar/restaurant_radar.db` — restaurants = 932 rows
(462 Brick & Mortar / 366 Food Truck / 104 Cafe), 8 distinct cities, hours present on 404 rows,
gas_stations = 40 rows (Pueblo 38, Pueblo West 2). Prices: `D:/Hermes_Core/Teams/Marketing/ops/offer_truth.json`
(`advertised_prices_usd` 9 and 199) and `PLACEMENT_TIERS` in `D:/Hermes_Core/Monetization/Restaurant_Radar/app.py`.

Honesty rule for this video: the map has no stop-level safety, amenity or review data today
(verified_at is empty on all 972 venue + fuel rows; review tables hold 0 rows). No scene, caption or
VO line may imply rated, inspected or reviewed stops.

Total runtime target: about 30 s.

| # | Asset (absolute path, exists on disk) | Headline (<=6 words) | Sub (<=10 words) | VO line (<=14 words) | Duration |
|---|---|---|---|---|---|
| 1 | `D:/Hermes_Core/workspace/Restaurant_Radar/promo/assets/hero.jpg` (real product screenshot; slow push-in on the I-25 pins) | Know what's open first | Live venue map for southern Colorado | Heading down I-25 hungry? Check what's open before you pull off. | 5 s |
| 2 | `D:/Hermes_Core/workspace/Restaurant_Radar/promo/assets/scenes/s2_venues.png` | 932 venues, one map | Restaurants, food trucks and cafes together | Nine hundred thirty-two restaurants, food trucks and cafes sit on one live map. | 5 s |
| 3 | `D:/Hermes_Core/workspace/Restaurant_Radar/promo/assets/scenes/s3_cities.png` | Eight cities along I-25 | Colorado Springs to Pueblo, plus 40 fuel stops | Eight cities from Colorado Springs to Pueblo, with forty fuel stops alongside. | 5 s |
| 4 | `D:/Hermes_Core/workspace/Restaurant_Radar/promo/assets/scenes/s4_hours.png` | Open or closed, right now | From published hours, never a guess | Where hours are published, the pin tells you open or closed right now. | 5 s |
| 5 | `D:/Hermes_Core/workspace/Restaurant_Radar/promo/assets/scenes/s5_pricing.png` | Own a venue? Get listed | Founding Professional $9/mo, first 10 venues | Own a Pueblo venue? Founding Professional is nine dollars a month. | 5 s |
| 6 (end-card) | `D:/Hermes_Core/workspace/Restaurant_Radar/promo/assets/scenes/s6_endcard.png` | restaurantradar.app | Free to search, no account needed | Open the live map at restaurantradar dot app. Free to search. | 5 s |

End-card on screen: **restaurantradar.app** + CTA **Open the live map** (button text from the landing page).

## Machine storyboard
Scenes 1-5 above plus the end-card CTA are encoded in
`D:/Hermes_Core/workspace/Restaurant_Radar/promo/video/storyboard.json` for
`D:/Hermes_Core/Teams/Marketing/video/make_promo_video.py` (its renderer draws the end-card from `cta`).
`--dry-run` returned `VALIDATION OK` on 2026-10-17; nothing has been rendered.

## Voice
Recommended edge-tts voice: **en-US-AndrewNeural** (Male; listed by `edge-tts --list-voices | grep en-US`
on this host 2026-10-17 as "Conversation, Copilot — Warm, Confident, Authentic, Honest"). Alternate:
en-US-EmmaNeural (Female, "Cheerful, Clear, Conversational").

Render each VO line separately so scene cuts land on line ends:

```bash
cd D:/Hermes_Core/workspace/Restaurant_Radar/promo/video
edge-tts --voice en-US-AndrewNeural --text "Heading down I-25 hungry? Check what's open before you pull off." --write-media vo1.mp3
```

## Assembly notes
- 16:9 master at 1280x720 from the scene PNGs (all 1280x720) and hero.jpg (1024x576, scale to fill).
- 9:16 for Shorts/Reels: centre-crop each scene, keep the left text block inside the safe area; the end-card URL must stay fully on screen.
- Burn captions from the Sub column; no music with lyrics.
- Do not add any rating stars, review quotes, badges or traffic numbers in the edit.
