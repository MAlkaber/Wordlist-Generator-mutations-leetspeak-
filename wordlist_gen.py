#!/usr/bin/env python3
"""
Wordlist Generator
=====================
Builds a targeted password wordlist from a small set of "seed" words
(names, pet names, company names, keywords scraped from a target) by
applying the same mutation patterns real users actually use when they
turn a memorable word into a "secure-looking" password.

Project 05 of a pentest/red-team learning portfolio.
Read README.md first for the concept walkthrough.

Usage:
    python3 wordlist_gen.py <seed1> [seed2 ...] [--years START END] [-o FILE]

Examples:
    python3 wordlist_gen.py summer password admin
    python3 wordlist_gen.py CompanyName --years 2020 2026 -o custom.txt
"""

import argparse
import itertools

# Only the substitutions people actually use in practice - not every
# theoretically possible one. Keeping this small is a deliberate choice:
# a wordlist with every combination of every substitution explodes into
# millions of entries that no real password will ever match.
LEET_MAP = {
    "a": ["4", "@"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["5", "$"],
    "t": ["7"],
}

COMMON_SUFFIXES = ["", "!", "1", "123", "!!", "1!", "@", "#"]
COMMON_PREFIXES = ["", "!"]


def case_variants(word: str) -> set[str]:
    """
    The handful of capitalization patterns real people actually use - not
    every possible case combination (that would be 2^len(word) and almost
    all of it garbage nobody would type). This is the difference between
    a *targeted* wordlist and a useless brute-force list: real humans are
    predictable.
    """
    if not word:
        return {word}
    return {word.lower(), word.upper(), word.capitalize()}


def leet_variants(word: str, max_variants: int = 6) -> set[str]:
    """
    Generate leetspeak substitutions for one word. Rather than
    substituting every possible character at once (combinatorial
    explosion for longer words), this generates one "substitute
    everything" pass plus a handful of single-character substitutions -
    since most real leetspeak passwords only swap the "obvious" letters,
    not every eligible one.
    """
    lower = word.lower()
    variants = {word}

    full_sub = "".join(
        LEET_MAP[c][0] if c in LEET_MAP else c for c in lower
    )
    variants.add(full_sub)

    for i, c in enumerate(lower):
        if c in LEET_MAP:
            for sub in LEET_MAP[c]:
                variants.add(lower[:i] + sub + lower[i + 1:])
                if len(variants) >= max_variants:
                    return variants

    return variants


def mutate_word(word: str, years: list[str]) -> set[str]:
    """Apply case variants, leet substitutions, and prefix/suffix combos to one seed word."""
    base_forms: set[str] = set()
    for cased in case_variants(word):
        base_forms |= leet_variants(cased)

    suffixes = COMMON_SUFFIXES + years
    results = set()
    for form in base_forms:
        for prefix, suffix in itertools.product(COMMON_PREFIXES, suffixes):
            results.add(f"{prefix}{form}{suffix}")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a targeted wordlist from seed words using common mutation patterns."
    )
    parser.add_argument("seeds", nargs="+", help="One or more seed words (names, keywords, etc.)")
    parser.add_argument(
        "--years", nargs=2, type=int, metavar=("START", "END"),
        help="Append a year range as suffixes too, e.g. --years 2015 2026",
    )
    parser.add_argument("-o", "--output", help="Write results to this file instead of stdout")
    args = parser.parse_args()

    years = [str(y) for y in range(args.years[0], args.years[1] + 1)] if args.years else []

    all_words: set[str] = set()
    for seed in args.seeds:
        all_words |= mutate_word(seed, years)

    sorted_words = sorted(all_words)

    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(sorted_words) + "\n")
        print(f"[+] Wrote {len(sorted_words)} candidate(s) to {args.output}")
    else:
        for w in sorted_words:
            print(w)
        print(f"\n[+] {len(sorted_words)} candidate(s) total")


if __name__ == "__main__":
    main()
