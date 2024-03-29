# General Usage
## Configuration
- Create a `.env` file with the following format:
    - `MAL_CLIENT_ID` can be created in https://myanimelist.net/apiconfig

```
MAL_CLIENT_ID=<>
```

## Running the file mapper

```
python file-mapper.py <path> [--type=] [--lang=] [--mal=] [--wikipedia=] [--prefill] [--debug]

--type=[anime]
  Simplify type matching telling the engine what type it should be using.

--lang=[en, ja]
  Simplify language matching telling the engine what language the 'path' name is writted in.

-------------- PREFILLABLE -----------------

--mal=[<url>]
  MAL episodes URL matching:
    - https://api.myanimelist.net/v2/anime?q={anime}&fields=alternative_titles

--wikipedia=[<url>]
  Wikipedia episodes URL matching:
    - https://en.wikipedia.org/wiki/List_of_{anime}_episodes
    - https://en.wikipedia.org/wiki/{anime}#Episode_list
```


## Running Tests

```
coverage run -m unittest discover
```

# Known Bugs
