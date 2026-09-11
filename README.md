# Wordlist Generator

**Project 05** of a pentest/red-team learning portfolio — see the [full roadmap](../ROADMAP.md).

Builds a small, *targeted* password wordlist from seed words (a
company name, a person's name, a season, anything gathered during
recon) by applying the mutation patterns real people actually use when
they turn a memorable word into a "secure-looking" password.

> ⚠️ Only use generated wordlists against accounts/systems you own or
> are explicitly authorized to test. Password guessing against real
> accounts you don't control is illegal and, against many services,
> will also lock out the legitimate user.

## Why targeted beats generic

Generic wordlists like `rockyou.txt` (14 million real leaked passwords)
are great for cracking hashes offline where speed is cheap. But for
**online** guessing — where every attempt might trigger a lockout or an
alert — you get maybe a few dozen tries. A list built from what you
actually know about the target (company name, product name, the season
it is, the CEO's dog's name from their Instagram) beats a generic list
by orders of magnitude in that situation, because real people build
passwords out of things that are personally memorable to *them*, not
random dictionary words.

## Concepts you need before reading the code

**Common human password patterns.** Decades of leaked password data
shows the same handful of transformations over and over:
`Capitalize` the first letter, append a `!` or a number, append the
current year, swap `a→4`, `e→3`, `i→1`, `o→0`, `s→5`. This tool
generates exactly those combinations — no more, no less. Real cracking
tools like hashcat and John the Ripper have entire *rule engines*
(`best64.rule`, `rockyou-30000.rule`) that do this same kind of
transformation, far more exhaustively — this project builds the same
idea from scratch so you understand what those rule files are actually
doing before you rely on them as a black box.

**Combinatorial explosion is the enemy, not the goal.** It's tempting
to generate *every* possible substitution/case/suffix combination — but
a 12-character word with 6 substitutable letters has 2⁶ = 64 leet
variants alone, times 3 case variants, times dozens of suffixes... you'd
have a wordlist too large to be useful, full of forms no human would
ever actually type. `leet_variants()` deliberately caps itself
(`max_variants`) instead of generating everything — a smaller, higher
quality list beats a huge low quality one, every time, for online
guessing.

## Code walkthrough

Open [`wordlist_gen.py`](wordlist_gen.py) alongside this section.

- **`case_variants()`** — just three forms per word: `lower`, `UPPER`,
  `Capitalize`. Deliberately *not* every 2ⁿ case combination.
- **`leet_variants()`** — one "substitute everything" pass, plus a
  handful of single-character substitutions, capped at `max_variants`.
- **`mutate_word()`** — combines case variants × leet variants ×
  prefix/suffix combos using `itertools.product()`, which generates
  every pairing of two (or more) iterables without you writing nested
  loops by hand — worth knowing well, it shows up constantly once you
  start generating combinations of anything.
- Sets (`set[str]`) are used throughout instead of lists specifically to
  get automatic deduplication for free — many mutation paths produce the
  same string (e.g. a word with no substitutable letters has the same
  "leet" and "normal" form), and we don't want duplicates bloating the
  output.

## Try it yourself (exercises)

1. Generate a wordlist from a company/product name you know plus a year
   range covering the last 5 years. How many candidates come out? Does
   that feel like a realistic number of attempts before a login would
   lock you out (typically 3-10 tries)? What does that tell you about
   how you'd actually *use* a list like this in practice (hint: order
   matters — which candidates would you try first)?
2. Add a `--separator` option that also tries common separators between
   word and suffix, like `word_2024` or `word-2024` (not just `word2024`).
3. Right now suffixes are simple strings. Add support for combining
   *two* seed words together (e.g. `summer` + `2024` seed word →
   `Summer2024!`, `summer.2024`, etc.) for targets that use two personal
   facts combined.
4. (Preview of Project 06) Once you have a wordlist, the next tool needs
   to actually try each candidate against a hash. Sketch what
   `hashlib.sha256(candidate.encode()).hexdigest()` would let you check.

## Running it

```bash
git clone <your-repo-url>
cd 05-wordlist-generator
python3 wordlist_gen.py summer --years 2023 2026
python3 wordlist_gen.py CompanyName ProductName --years 2020 2026 -o custom.txt
```

Standard library only — no `pip install` needed.

## What's next

**Project 06 — Hash Identifier & Dictionary Cracker:** take a wordlist
like the one this tool generates and actually test it against a hash,
while also learning to recognize hash types (MD5 vs SHA1 vs SHA256 vs
bcrypt) by their length and format.
