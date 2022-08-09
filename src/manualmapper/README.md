# General Usage
## Configuration
- Create a `.env` file with the following format:
    - `MAL_CLIENT_ID` can be created in https://myanimelist.net/apiconfig

```
MAL_CLIENT_ID=<>
```

## Running the manual mapper

```
python file-mapper.py <path> [--debug]
```

## Running Tests

```
coverage run -m unittest discover
```

# Known Bugs
