# Contributing

Thank you for helping QuranLingo's voices sound better.

## Rules that never change

- Quranic verses are never synthesised. They come from licensed human recitation.
- Only models whose licence allows commercial use.
- One engine and one fixed voice per character per language. Never mix engines for the same character.
- All voices are synthetic. Never clone a real person's voice.
- Stories are told by a narrator. No character speaks as a prophet.
- No em dashes or en dashes in code comments, docs or messages.

## Test first

1. Write a test for the behaviour you want, in `tests/`.
2. Run it and see it fail for the right reason: `uv run --project analysis python -m pytest`
3. Commit the failing test (message starts with `test:` and ends with `(red)`).
4. Write the code until every test passes.
5. Commit (message starts with `feat:` or `fix:` and ends with `(green)`).

Code that needs a model loaded (the `engines/*/` scripts) stays thin: put the logic in `tools/`, where it can be tested without a model.

## Never commit

The answer keys (`keys/`), generated audio (`outputs/`, `voices/`), or QuranLingo's spreadsheet. `.gitignore` already excludes them.
