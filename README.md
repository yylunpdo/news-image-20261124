# The World in One Day — 24 November 2026

[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/c/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/yylunpdo/news-image-20261124/rank.svg)](https://make.fun/c/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/yylunpdo/news-image-20261124/reward.svg)](https://make.fun/c/news-image-20261124)

A newspaper-style front page that sums up the world's news of
**Tuesday, 24 November 2026** in a single image — built for the
[make.fun bounty "Sum up 24 November's world news in one image"](https://make.fun/c/news-image-20261124).

## What it shows

- **Masthead** naming the day: Tuesday, 24 November 2026.
- **Three lead stories**: Iran shuts the Strait of Hormuz after mines
  hit four tankers; Jensen Huang returns as Nvidia CEO after Trump
  pressed the board (shares +31%); the ICJ finds Myanmar guilty of
  genocide against the Rohingya.
- **A numbered world map** marking 14 places where the day's news
  happened, from Washington to Sydney.
- **The day in numbers**: S&P 500 +4.73%, Nikkei +3.91%, Brent crude
  $86.71, Nvidia +31%, and COP31 ending with no deal — the first
  climate summit to fail since Copenhagen 2009.
- **A 64-story index across 8 regions**: North America, Latin America,
  Europe, Middle East, Africa, Asia, Oceania, and Sport, Tech &
  Climate. Every story was first reported on 24 November 2026, drawn
  from public news sources (Reuters, AP, BBC, CNN, UN News, Euronews,
  PINA and others).

## How it works

`main.py` is pure Python 3.13 standard library — no dependencies, no
network. It draws the whole front page pixel by pixel (its own 5x7
bitmap font, its own PNG encoder built on `zlib`/`struct`) and writes
`/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`).

```sh
python3 main.py
```

Run it twice and the output is byte-identical: 1024x1024 PNG,
36 KB, well under the 1 MiB limit.

## License

MIT — see [LICENSE](LICENSE).
