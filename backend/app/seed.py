from sqlalchemy import select

from app.database import async_session
from app.models import Product, MarketplaceLink, TCG, Category, Marketplace

# Cardmarket URL helpers
_CM_POKEMON = "https://www.cardmarket.com/en/Pokemon/Products"
_CM_MAGIC = "https://www.cardmarket.com/en/Magic/Products"


def _cm_pokemon(cat: str, slug: str) -> str:
    return f"{_CM_POKEMON}/{cat}/{slug}"


def _cm_magic(cat: str, slug: str) -> str:
    return f"{_CM_MAGIC}/{cat}/{slug}"


SAMPLE_PRODUCTS = [
    # ==================== POKEMON TCG 2023 ====================
    {
        "name": "Scarlet & Violet Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Scarlet & Violet",
        "set_code": "SV1",
        "release_date": "2023-03-31",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Scarlet-Violet-Booster-Box"), "external_id": "692092"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CJC2MH21", "external_id": "B0CJC2MH21"},
            {"marketplace": Marketplace.GEIZHALS, "url": "https://geizhals.de/pokemon-sammelkartenspiel-karmesin-purpur-top-trainer-box-a2951578.html", "external_id": "2951578"},
        ],
    },
    {
        "name": "Scarlet & Violet Koraidon Elite Trainer Box",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Scarlet & Violet",
        "set_code": "SV1",
        "release_date": "2023-03-31",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Elite-Trainer-Boxes", "Scarlet-Violet-Koraidon-Elite-Trainer-Box"), "external_id": "692101"},
        ],
    },
    {
        "name": "Paldea Evolved Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Paldea Evolved",
        "set_code": "SV2",
        "release_date": "2023-06-09",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Paldea-Evolved-Booster-Box"), "external_id": "703156"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CKT2SWX5", "external_id": "B0CKT2SWX5"},
        ],
    },
    {
        "name": "Paldea Evolved Elite Trainer Box",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Paldea Evolved",
        "set_code": "SV2",
        "release_date": "2023-06-09",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Elite-Trainer-Boxes", "Paldea-Evolved-Elite-Trainer-Box"), "external_id": "703175"},
        ],
    },
    {
        "name": "Obsidian Flames Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Obsidian Flames",
        "set_code": "SV3",
        "release_date": "2023-08-11",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Obsidian-Flames-Booster-Box"), "external_id": "715465"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0C6D9YN1J", "external_id": "B0C6D9YN1J"},
        ],
    },
    {
        "name": "Pokémon Card 151 Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Pokémon Card 151",
        "set_code": "SV3pt5",
        "release_date": "2023-09-22",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Pokemon-Card-151-Booster-Box"), "external_id": "718514"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0BT15FD3J", "external_id": "B0BT15FD3J"},
        ],
    },
    {
        "name": "151 Elite Trainer Box",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Pokémon Card 151",
        "set_code": "SV3pt5",
        "release_date": "2023-09-22",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Elite-Trainer-Boxes", "151-Elite-Trainer-Box"), "external_id": "719691"},
        ],
    },
    {
        "name": "151 Ultra-Premium Collection",
        "tcg": TCG.POKEMON,
        "category": Category.COLLECTION_BOX,
        "set_name": "Pokémon Card 151",
        "set_code": "SV3pt5",
        "release_date": "2023-10-06",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Box-Sets", "151-Ultra-Premium-Collection"), "external_id": "719698"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CD7PKZSK", "external_id": "B0CD7PKZSK"},
        ],
    },
    {
        "name": "151 Booster Bundle",
        "tcg": TCG.POKEMON,
        "category": Category.BUNDLE,
        "set_name": "Pokémon Card 151",
        "set_code": "SV3pt5",
        "release_date": "2023-09-22",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "151-Booster-Bundle"), "external_id": "719695"},
        ],
    },
    {
        "name": "Paradox Rift Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Paradox Rift",
        "set_code": "SV4",
        "release_date": "2023-11-03",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Paradox-Rift-Booster-Box"), "external_id": "728718"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D5PV25GL", "external_id": "B0D5PV25GL"},
        ],
    },

    # ==================== POKEMON TCG 2024 ====================
    {
        "name": "Paldean Fates Elite Trainer Box",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Paldean Fates",
        "set_code": "SV4pt5",
        "release_date": "2024-01-26",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Elite-Trainer-Boxes", "Paldean-Fates-Elite-Trainer-Box"), "external_id": "745548"},
        ],
    },
    {
        "name": "Paldean Fates Booster Bundle",
        "tcg": TCG.POKEMON,
        "category": Category.BUNDLE,
        "set_name": "Paldean Fates",
        "set_code": "SV4pt5",
        "release_date": "2024-01-26",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Paldean-Fates-Booster-Bundle"), "external_id": "745565"},
        ],
    },
    {
        "name": "Temporal Forces Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Temporal Forces",
        "set_code": "SV5",
        "release_date": "2024-03-22",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Temporal-Forces-Booster-Box"), "external_id": "750403"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CS33S7BJ", "external_id": "B0CS33S7BJ"},
        ],
    },
    {
        "name": "Twilight Masquerade Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Twilight Masquerade",
        "set_code": "SV6",
        "release_date": "2024-05-24",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Twilight-Masquerade-Booster-Box"), "external_id": "761219"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DDT137S3", "external_id": "B0DDT137S3"},
        ],
    },
    {
        "name": "Shrouded Fable Booster Bundle",
        "tcg": TCG.POKEMON,
        "category": Category.BUNDLE,
        "set_name": "Shrouded Fable",
        "set_code": "SV6pt5",
        "release_date": "2024-08-02",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Shrouded-Fable-Booster-Bundle-Version-1"), "external_id": "770954"},
        ],
    },
    {
        "name": "Stellar Crown Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Stellar Crown",
        "set_code": "SV7",
        "release_date": "2024-09-13",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Stellar-Crown-Booster-Box"), "external_id": "776325"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D81PVDR1", "external_id": "B0D81PVDR1"},
        ],
    },
    {
        "name": "Stellar Crown Elite Trainer Box",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Stellar Crown",
        "set_code": "SV7",
        "release_date": "2024-09-13",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Elite-Trainer-Boxes", "Stellar-Crown-Elite-Trainer-Box"), "external_id": "776336"},
        ],
    },
    {
        "name": "Surging Sparks Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Surging Sparks",
        "set_code": "SV8",
        "release_date": "2024-11-08",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Surging-Sparks-Booster-Box"), "external_id": "784949"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DFBGYFD3", "external_id": "B0DFBGYFD3"},
            {"marketplace": Marketplace.IDEALO, "url": "https://www.idealo.de/preisvergleich/OffersOfProduct/203385194_-pokemon-karmesin-purpur-funkenflug-display-36-booster-packs-pokemon.html", "external_id": "203385194"},
            {"marketplace": Marketplace.GEIZHALS, "url": "https://geizhals.de/pokemon-sammelkartenspiel-karmesin-purpur-funkenflug-display-36-booster-packs-a3289009.html", "external_id": "3289009"},
        ],
    },
    {
        "name": "Surging Sparks Elite Trainer Box",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Surging Sparks",
        "set_code": "SV8",
        "release_date": "2024-11-08",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Elite-Trainer-Boxes", "Surging-Sparks-Elite-Trainer-Box"), "external_id": "784963"},
        ],
    },

    # ==================== POKEMON TCG 2025 ====================
    {
        "name": "Prismatic Evolutions Booster Bundle",
        "tcg": TCG.POKEMON,
        "category": Category.BUNDLE,
        "set_name": "Prismatic Evolutions",
        "set_code": "SV8pt5",
        "release_date": "2025-01-17",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Prismatic-Evolutions-Booster-Bundle"), "external_id": "798924"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DN98RVZM", "external_id": "B0DN98RVZM"},
            {"marketplace": Marketplace.IDEALO, "url": "https://www.idealo.de/preisvergleich/OffersOfProduct/203791818_-pokemon-karmesin-purpur-prismatische-entwicklungen-booster-bundle-pokemon.html", "external_id": "203791818"},
            {"marketplace": Marketplace.GEIZHALS, "url": "https://geizhals.de/pokemon-sammelkartenspiel-karmesin-purpur-prismatische-entwicklungen-booster-bundle-6-booster-packs-a3350413.html", "external_id": "3350413"},
        ],
    },
    {
        "name": "Prismatic Evolutions Elite Trainer Box",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Prismatic Evolutions",
        "set_code": "SV8pt5",
        "release_date": "2025-01-17",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Elite-Trainer-Boxes", "Prismatic-Evolutions-Elite-Trainer-Box"), "external_id": "798930"},
        ],
    },
    {
        "name": "Prismatic Evolutions Super-Premium Collection",
        "tcg": TCG.POKEMON,
        "category": Category.COLLECTION_BOX,
        "set_name": "Prismatic Evolutions",
        "set_code": "SV8pt5",
        "release_date": "2025-01-17",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Box-Sets", "Prismatic-Evolutions-Super-Premium-Collection"), "external_id": "813966"},
        ],
    },
    {
        "name": "Journey Together Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Journey Together",
        "set_code": "SV9",
        "release_date": "2025-03-28",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Booster-Boxes", "Journey-Together-Booster-Box"), "external_id": "805579"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0F1GXTFGL", "external_id": "B0F1GXTFGL"},
            {"marketplace": Marketplace.IDEALO, "url": "https://www.idealo.de/preisvergleich/OffersOfProduct/204548857_-pokemon-karmesin-purpur-gemeinsam-staerker-display-36-booster-packs-pokemon.html", "external_id": "204548857"},
            {"marketplace": Marketplace.GEIZHALS, "url": "https://geizhals.de/pokemon-sammelkartenspiel-karmesin-purpur-gemeinsam-staerker-display-36-booster-packs-a3388486.html", "external_id": "3388486"},
        ],
    },
    {
        "name": "Journey Together Elite Trainer Box",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Journey Together",
        "set_code": "SV9",
        "release_date": "2025-03-28",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_pokemon("Elite-Trainer-Boxes", "Journey-Together-Elite-Trainer-Box"), "external_id": "805593"},
        ],
    },

    # ==================== MAGIC: THE GATHERING 2023 ====================
    {
        "name": "The Lord of the Rings: Tales of Middle-earth Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "The Lord of the Rings: Tales of Middle-earth",
        "set_code": "LTR",
        "release_date": "2023-06-23",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "The-Lord-of-the-Rings-Tales-of-Middle-earth-Draft-Booster-Box"), "external_id": "698913"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0BVT3ZL13", "external_id": "B0BVT3ZL13"},
        ],
    },
    {
        "name": "Wilds of Eldraine Collector Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Wilds of Eldraine",
        "set_code": "WOE",
        "release_date": "2023-09-08",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Wilds-of-Eldraine-Collector-Booster-Box"), "external_id": "719684"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0C3T4VZN8", "external_id": "B0C3T4VZN8"},
        ],
    },
    {
        "name": "The Lost Caverns of Ixalan Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "The Lost Caverns of Ixalan",
        "set_code": "LCI",
        "release_date": "2023-11-17",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "The-Lost-Caverns-of-Ixalan-Draft-Booster-Box"), "external_id": "734176"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CGK771H1", "external_id": "B0CGK771H1"},
        ],
    },

    # ==================== MAGIC: THE GATHERING 2024 ====================
    {
        "name": "Murders at Karlov Manor Play Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Murders at Karlov Manor",
        "set_code": "MKM",
        "release_date": "2024-02-09",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Murders-at-Karlov-Manor-Play-Booster-Box"), "external_id": "748053"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CMR46LJC", "external_id": "B0CMR46LJC"},
        ],
    },
    {
        "name": "Murders at Karlov Manor Fat Pack Bundle",
        "tcg": TCG.MAGIC,
        "category": Category.BUNDLE,
        "set_name": "Murders at Karlov Manor",
        "set_code": "MKM",
        "release_date": "2024-02-09",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Bundles", "Murders-at-Karlov-Manor-Fat-Pack-Bundle"), "external_id": "748054"},
        ],
    },
    {
        "name": "Outlaws of Thunder Junction Play Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Outlaws of Thunder Junction",
        "set_code": "OTJ",
        "release_date": "2024-04-19",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Outlaws-of-Thunder-Junction-Play-Booster-Box"), "external_id": "758329"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CTKVW1KY", "external_id": "B0CTKVW1KY"},
        ],
    },
    {
        "name": "Modern Horizons 3 Play Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Modern Horizons 3",
        "set_code": "MH3",
        "release_date": "2024-06-14",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Modern-Horizons-3-Play-Booster-Box"), "external_id": "758482"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CTLT5DJQ", "external_id": "B0CTLT5DJQ"},
            {"marketplace": Marketplace.IDEALO, "url": "https://www.idealo.de/preisvergleich/OffersOfProduct/203092166_-magic-the-gathering-modern-horizons-3-play-booster-display-36-booster-packs-wizards-of-the-coast.html", "external_id": "203092166"},
            {"marketplace": Marketplace.GEIZHALS, "url": "https://geizhals.de/magic-the-gathering-modern-horizons-3-play-booster-display-36-packs-a3240783.html", "external_id": "3240783"},
        ],
    },
    {
        "name": "Modern Horizons 3 Collector Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Modern Horizons 3",
        "set_code": "MH3",
        "release_date": "2024-06-14",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Modern-Horizons-3-Collector-Booster-Box"), "external_id": "758483"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CTLL4PMF", "external_id": "B0CTLL4PMF"},
        ],
    },
    {
        "name": "Bloomburrow Play Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Bloomburrow",
        "set_code": "BLB",
        "release_date": "2024-08-02",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Bloomburrow-Play-Booster-Box"), "external_id": "774109"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CTKMFZD7", "external_id": "B0CTKMFZD7"},
        ],
    },
    {
        "name": "Duskmourn: House of Horror Play Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Duskmourn: House of Horror",
        "set_code": "DSK",
        "release_date": "2024-09-27",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Duskmourn-House-of-Horror-Play-Booster-Box"), "external_id": "776443"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D68Z1YCS", "external_id": "B0D68Z1YCS"},
        ],
    },
    {
        "name": "Magic: The Gathering Foundations Play Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Foundations",
        "set_code": "FDN",
        "release_date": "2024-11-15",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Magic-The-Gathering-Foundations-Play-Booster-Box"), "external_id": "781940"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D9KYV7B8", "external_id": "B0D9KYV7B8"},
        ],
    },
    {
        "name": "Magic: The Gathering Foundations Collector Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Foundations",
        "set_code": "FDN",
        "release_date": "2024-11-15",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Magic-The-Gathering-Foundations-Collector-Booster-Box"), "external_id": "781941"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D9KZ7MRG", "external_id": "B0D9KZ7MRG"},
        ],
    },

    # ==================== MAGIC: THE GATHERING 2025 ====================
    {
        "name": "Aetherdrift Play Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Aetherdrift",
        "set_code": "DFT",
        "release_date": "2025-02-14",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Aetherdrift-Play-Booster-Box"), "external_id": "803868"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DNV3NV61", "external_id": "B0DNV3NV61"},
        ],
    },
    {
        "name": "Tarkir: Dragonstorm Play Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Tarkir: Dragonstorm",
        "set_code": "TDM",
        "release_date": "2025-04-11",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": _cm_magic("Booster-Boxes", "Tarkir-Dragonstorm-Play-Booster-Box"), "external_id": "813081"},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DSQZC4PB", "external_id": "B0DSQZC4PB"},
        ],
    },
]


async def seed_sample_products():
    async with async_session() as session:
        result = await session.execute(select(Product).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        for data in SAMPLE_PRODUCTS:
            links_data = data.pop("links", [])
            product = Product(**data)
            session.add(product)
            await session.flush()

            for link_data in links_data:
                link = MarketplaceLink(
                    product_id=product.id,
                    marketplace=link_data["marketplace"],
                    url=link_data["url"],
                    external_id=link_data.get("external_id", ""),
                )
                session.add(link)

        await session.commit()
