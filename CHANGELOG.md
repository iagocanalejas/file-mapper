# Changelog

## [0.2.0] - 2022-08-
- refactor: move engine presets to `GlobalConfig` singleton
- refactor: items are now only parsed once

## [0.1.0] - 2022-07-22
- refactor: datasource metadata management
- refactor: improve error handling
- refactor: change anilist to work as a graphql API
- refactor: wikipedia scrapper async load
- refactor: change `mal_id` to `datasource_id`
- refactor: split responsibility and change process sequence


- feat: implement IMDB API, scrapper and Wikipedia fallback
- feat: add language input to pre-set the item name language
- feat: add setup.py to make the package installable
- feat: implement .X recap episodes
- feat: language matching for anime APIs
- feat: add meaningful season names to episode name
- feat: improve season parsing from wikipedia
- feat: implement anilist API
- feat: support episode/seasons without name if they are in a show


- fix: season chapters not matching because of the episode number
- fix: output name having invalid characters
- fix: data retrieved from a trusted source shouldn't be title-cased
- fix: split requirements
- fix: `parser` and `formatter` types not being recognized in processor subclasses


## [0.0.0] - 2022-06-18
- anime file mapper
- initial commit
