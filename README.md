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