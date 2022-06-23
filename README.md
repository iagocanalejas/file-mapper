# General Usage

- Create a `.env` file with the following format:
    - `MAL_CLIENT_ID` can be created in https://myanimelist.net/apiconfig

```
MAL_CLIENT_ID=<>
```

- Run

```
python main.py <path> [--type] [--debug]
```

- Examples

```
python main.py tests/_manual/files/ --debug
python main.py tests/_manual/seasons/\[Judas\]\ Ahiru\ no\ Sora\ \(Season\ 1\)\ \[1080p\]\[HEVC\ x265\ 10bit\]\[Multi-Subs\]/ --debug
python main.py tests/_manual/shows/\[Anipakku\]\ Overlord\ \(S01\ S02\ S03\ +\ Movies\ +\ OVA\ +\ Specials\)\ \[BD\ 1080p\]\[HEVC\ x265\ 10bit\]\[Multi-Dub\]\[Multi-Subs\]/ --debug
```

# Running Tests

```
coverage run -m unittest discover
```

# Known Bugs

## Datasource

### MAL

- For some anime queries the result makes no sense

```
(examples):

Seikon no Qwaser -> Seikon no Qwaser II
```