# The Passport Page of a Country That Isn't There

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Ryukein19/passport-country/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Ryukein19/passport-country/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A program that writes one image to `/output/entry.png`: an open passport
spread for the invented Republic of Solmarra — a harbour island nation
reachable only by sea. The holder is Mara Ilse Kaldris, a licensed
ferry captain (licence F-0217).

The data page carries a photorealistic portrait (`portrait.jpg`, loaded
by the program), a faint ghost image of the same portrait, bilingual
data rows including the holder's profession and licence, a PERSONAL NO.
field (Nordic-style personnummer, 030979-4821, also carried in the
MRZ optional-data field), the holder's signature, observations, a
VISA-FREE TRAVEL box (Dravnia · Kessara · 90 days), a microtext motto
line ("PER MARE · PER LUCEM", the national motto, repeated in 8 pt
type — the microprinting real passports carry), a repeating security
strip, and a machine-readable zone ENCLOSED IN A BOX — all over a wavy
guilloche security background plus a large circular guilloche. The
passport number (SLM517204) is repeated at the top right in red and
at the foot of both pages.

The visa page carries a full structured DRAVNIA VISITOR VISA box
(Type C, single entry, 30 days, valid 01 MAR – 30 APR 2024, fee
40 DRV) with a barcode strip at its foot, eight stamps from
neighbouring ports — two of them ROUND, the rest rectangular — all
dated after the passport's 09 FEB 2024 issue date (the Dravnia pair
falls inside the visa's validity), a structured FERRY ROUTE
ENDORSEMENT box (routes, season, Harbourmaster report, captain's
licence), a red "ARRIVAL BY SEA ONLY — NO AIRPORT IN SOLMARRA"
stamp, a round "FERRY FEE PAID — 12 SOL" fee stamp, and a national
harbour motif at the foot of the page — the Port Solmar lighthouse
over waves, the national-character artwork real passport visa pages
carry (ICAO Doc 9303).

v5 is a clean-up, not a detail pile-up: v2/v3/v4 all scored in the
500s, and the detail additions moved the score by only ±10k, while
the top entries are clean and spacious. So v5 removes the CONDITIONS
block, opens up the spacing, and adds the structural features the top
entries carry: personal number, boxed MRZ, repeated passport number,
visa-free travel, barcode, round stamps, circular guilloche.

Run with `python3 main.py` (Pillow preferred; a pure-stdlib fallback renders
a simplified version of the same spread if Pillow is unavailable).
