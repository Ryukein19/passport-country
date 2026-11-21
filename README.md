# The Passport Page of a Country That Isn't There

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Ryukein19/passport-country/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Ryukein19/passport-country/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A program that writes one image to `/output/entry.png`: an open passport
spread for the invented Republic of Solmarra — a harbour island nation
reachable only by sea. The data page carries a photorealistic portrait
(`portrait.jpg`, loaded by the program), bilingual data rows, the
holder's signature, an observation about the Solmaran tide tables, and
a machine-readable zone. The visa page carries eight stamps from
neighbouring ports, all dated after the passport's 09 FEB 2024 issue
date, a Conditions of Issue box (outer isles closed November–March
without a Lighthouse Office licence), a red "ARRIVAL BY SEA ONLY — NO
AIRPORT IN SOLMARRA" stamp, and a round "FERRY PASSAGE PAID — 12 SOL"
fee stamp.

Run with `python3 main.py` (Pillow preferred; a pure-stdlib fallback renders
a simplified version of the same spread if Pillow is unavailable).
