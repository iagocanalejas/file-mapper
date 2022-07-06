import os
from typing import List

from src.matchers import MediaType
from tests.factories import EpisodeFactory, SeasonFactory, ShowFactory
from tests.settings import MAL_FIXTURES_DIR, ANILIST_FIXTURES_DIR, WIKIPEDIA_FIXTURES_DIR
from tests.utils import TestObject

# noinspection LongLine
TEST_OBJECTS: List[TestObject] = [
    TestObject(
        item=EpisodeFactory.create(item_name='[Judas] Ahiru no Sora - S01E01.mkv'),
        media_type=MediaType.ANIME,
        expected_names=['Ahiru no Sora - 01 - The Ugly Duckling.mkv'],
        fixtures=[
            (r're:.*myanimelist.*anime\?q=Ahiru%20no%20Sora', f"json:{os.path.join(MAL_FIXTURES_DIR, 'ahiru_no_sora.json')}"),
            (r're:.*myanimelist.*anime\/37403', f"json:{os.path.join(MAL_FIXTURES_DIR, 'ahiru_no_sora_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'ahiru_no_sora_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'ahiru_no_sora_details.json')}"),
            (r're:.*wikipedia.*\/List_of_Ahiru_no_Sora_episodes', None),  # Requires an empty response to use main_page load
            (r're:.*wikipedia.*\/Ahiru_no_Sora#Episode_list', f"html:{os.path.join(WIKIPEDIA_FIXTURES_DIR, 'main_page_ahiru_no_sora.html')}"),
        ],
    ),
    TestObject(
        item=EpisodeFactory.create(item_name='[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv'),
        media_type=MediaType.ANIME,
        expected_names=['Great Pretender - 02 - Case1_2: Los Angeles Connection.mkv'],
        fixtures=[
            (r're:.*myanimelist.*anime\?q=Great%20Pretender', f"json:{os.path.join(MAL_FIXTURES_DIR, 'great_pretender.json')}"),
            (r're:.*myanimelist.*anime\/40052', f"json:{os.path.join(MAL_FIXTURES_DIR, 'great_pretender_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'great_pretender_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'great_pretender_details.json')}"),
            (r're:.*wikipedia.*\/List_of_Great_Pretender_episodes', f"html:{os.path.join(WIKIPEDIA_FIXTURES_DIR, 'episode_page_great_pretender.html')}"),
        ],
    ),
    TestObject(
        item=EpisodeFactory.create(item_name='[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv'),
        media_type=MediaType.ANIME,
        expected_names=['Tate no Yuusha no Nariagari Season 2 - 08 - A Parting in the Snow.mkv'],
        fixtures=[
            (r're:.*myanimelist.*anime\?q=Tate%20no%20Yuusha%20no%20Nariagari', f"json:{os.path.join(MAL_FIXTURES_DIR, 'tate_no_yuusha.json')}"),
            (r're:.*myanimelist.*anime\/40356', f"json:{os.path.join(MAL_FIXTURES_DIR, 'tate_no_yuusha_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'tate_no_yuusha_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'tate_no_yuusha_details.json')}"),
            (r're:.*wikipedia.*\/List_of_The_Rising_of_the_Shield_Hero_episodes', f"html:{os.path.join(WIKIPEDIA_FIXTURES_DIR, 'episode_page_tate_no_yuusha.html')}"),
        ],
    ),
    TestObject(
        item=EpisodeFactory.create(item_name='[Cerberus] Seikon no Qwaser II - S02E01 - [7102F4EE].mkv'),
        media_type=MediaType.ANIME,
        expected_names=['Seikon no Qwaser II - 01 - Silver Princess of the Lilies.mkv'],
        fixtures=[
            (r're:.*myanimelist.*anime\?q=Seikon%20no%20Qwaser', f"json:{os.path.join(MAL_FIXTURES_DIR, 'seikon_no_qwaser.json')}"),
            (r're:.*myanimelist.*anime\/10073', f"json:{os.path.join(MAL_FIXTURES_DIR, 'seikon_no_qwaser_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'seikon_no_qwaser_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'seikon_no_qwaser_details.json')}"),
            (r're:.*wikipedia.*\/List_of_The_Qwaser_of_Stigmata_episodes', f"html:{os.path.join(WIKIPEDIA_FIXTURES_DIR, 'episode_page_seikon_no_qwaser.html')}"),
        ],
    ),
    # TODO: not working because we need to use 'Ice' instead of 'ICE' for wikipedia. We can't just titlecase the words because it will also break
    # TestObject(
    #     item=EpisodeFactory.create(item_name='[PuyaSubs!] Yuri!!! On ICE - 11 [720p][663F641B].mkv'),
    #     media_type=MediaType.ANIME,
    #     expected_name=['Yuri!!! On ICE - 11 - Gotta Super-Supercharge it! Grand Prix Final Short Program.mkv'],
    #     fixtures=[
    #         (r're:.*myanimelist.*anime\?q=Yuri!!!%20On%20ICE', f"json:{os.path.join(MAL_FIXTURES_DIR, 'yuri_on_ice.json')}"),
    #         (r're:.*myanimelist.*anime\/32995', f"json:{os.path.join(MAL_FIXTURES_DIR, 'yuri_on_ice_details.json')}"),
    #         ('anilist:get_anime', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'yuri_on_ice_details.json')}"),
    #         ('anilist:get_anime_id', 'int:21709'),
    #         ('anilist:get_anime_with_id', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'yuri_on_ice_details.json')}"),
    #         (r're:.*wikipedia.*\/List_of_Yuri_on_Ice_episodes', f"html:{os.path.join(WIKIPEDIA_FIXTURES_DIR, 'episode_page_yuri_on_ice.html')}"),
    #     ],
    # ),

    ########################
    #       Seasons        #
    ########################
    TestObject(
        item=SeasonFactory.create(
            item_name='[Judas] Ahiru no Sora (Season 1) [1080p][HEVC x265 10bit][Multi-Subs]',
            episodes=[
                EpisodeFactory.create(item_name='[Judas] Ahiru no Sora - S01E01.mkv'),
                EpisodeFactory.create(item_name='[Judas] Ahiru no Sora - S01E02.mkv'),
                EpisodeFactory.create(item_name='[Judas] Ahiru no Sora - S01E03.mkv'),
                EpisodeFactory.create(item_name='[Judas] Ahiru no Sora - S01E04.mkv'),
            ]
        ),
        media_type=MediaType.ANIME,
        expected_names=[
            'Ahiru no Sora',
            'Ahiru no Sora - 01 - The Ugly Duckling.mkv',
            'Ahiru no Sora - 02 - Boys Without Talent.mkv',
            'Ahiru no Sora - 03 - Momoharu\'s Wings.mkv',
            'Ahiru no Sora - 04 - First Flight.mkv',
        ],
        fixtures=[
            (r're:.*myanimelist.*anime\?q=Ahiru%20no%20Sora', f"json:{os.path.join(MAL_FIXTURES_DIR, 'ahiru_no_sora.json')}"),
            (r're:.*myanimelist.*anime\/37403', f"json:{os.path.join(MAL_FIXTURES_DIR, 'ahiru_no_sora_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'ahiru_no_sora_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'ahiru_no_sora_details.json')}"),
            (r're:.*wikipedia.*\/List_of_Ahiru_no_Sora_episodes', None),  # Requires an empty response to use main_page load
            (r're:.*wikipedia.*\/Ahiru_no_Sora#Episode_list', f"html:{os.path.join(WIKIPEDIA_FIXTURES_DIR, 'main_page_ahiru_no_sora.html')}"),
        ],
    ),

    ########################
    #        Shows         #
    ########################
    TestObject(
        item=ShowFactory.create(
            item_name='Hajime no Ippo',
            seasons=[
                SeasonFactory.create(item_name='season 1', episodes=[
                    EpisodeFactory.create(item_name='S1E01 [DVDRip 640x480 HEVC x265 10bit OPUS].mkv'),
                    EpisodeFactory.create(item_name='S1E02 [DVDRip 640x480 HEVC x265 10bit OPUS].mkv'),
                ]),
                SeasonFactory.create(item_name='season 2', episodes=[
                    EpisodeFactory.create(item_name='S2E01 [DVDRip 640x480 HEVC x265 10bit OPUS].mkv'),
                    EpisodeFactory.create(item_name='S2E02 [DVDRip 640x480 HEVC x265 10bit OPUS].mkv'),
                ]),
            ],
        ),
        media_type=MediaType.ANIME,
        expected_names=[
            'Hajime no Ippo',
            'Hajime no Ippo',
            'Hajime no Ippo - 01 - The First Step.mkv',
            'Hajime no Ippo - 02 - Fruits of Labor.mkv',
            'Hajime no Ippo Season 2: New Challenger (2009)',
            'Hajime no Ippo - 01 - The New Step.mkv',  # TODO: should contain season
            'Hajime no Ippo - 02 - Bloody Cross.mkv',
        ],
        fixtures=[
            (r're:.*myanimelist.*anime\?q=Hajime%20no%20Ippo', f"json:{os.path.join(MAL_FIXTURES_DIR, 'hajime_no_ippo.json')}"),
            (r're:.*myanimelist.*anime\/263', f"json:{os.path.join(MAL_FIXTURES_DIR, 'hajime_no_ippo_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'hajime_no_ippo_details.json')}"),
            (r're:.*graphql\.anilist.*', f"json:{os.path.join(ANILIST_FIXTURES_DIR, 'hajime_no_ippo_details.json')}"),
            (r're:.*wikipedia.*', None),  # Requires an empty response to use main_page load
            (r're:.*wikipedia.*', None),  # Requires an empty response to use japanese load
            (r're:.*wikipedia.*\/List_of_Hajime_no_Ippo_episodes', f"html:{os.path.join(WIKIPEDIA_FIXTURES_DIR, 'episode_page_hajime_no_ippo.html')}"),
        ],
    ),
]
