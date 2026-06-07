from sqlalchemy import select

from app.database import async_session
from app.models import Product, MarketplaceLink, TCG, Category, Marketplace

SAMPLE_PRODUCTS = [
    # ==================== POKEMON TCG 2023 ====================
    {
        "name": "Scarlet & Violet Base Set Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Scarlet & Violet",
        "set_code": "SV1",
        "release_date": "2023-03-31",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0BV6B5Z79", "external_id": "B0BV6B5Z79"},
        ],
    },
    {
        "name": "Scarlet & Violet Base Set ETB",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Scarlet & Violet",
        "set_code": "SV1",
        "release_date": "2023-03-31",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Elite-Trainer-Boxes/Scarlet-Violet-Elite-Trainer-Box", "external_id": ""},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Paldea-Evolved-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0C1PLXY4D", "external_id": "B0C1PLXY4D"},
        ],
    },
    {
        "name": "Paldea Evolved ETB",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Paldea Evolved",
        "set_code": "SV2",
        "release_date": "2023-06-09",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Elite-Trainer-Boxes/Scarlet-Violet-Paldea-Evolved-Elite-Trainer-Box", "external_id": ""},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Obsidian-Flames-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0C1PMG2GF", "external_id": "B0C1PMG2GF"},
        ],
    },
    {
        "name": "Pokemon 151 Booster Box (EN)",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Pokemon Card 151",
        "set_code": "SV3pt5",
        "release_date": "2023-09-22",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-151-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0C7T5WV3P", "external_id": "B0C7T5WV3P"},
        ],
    },
    {
        "name": "Pokemon 151 ETB",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Pokemon Card 151",
        "set_code": "SV3pt5",
        "release_date": "2023-09-22",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Elite-Trainer-Boxes/Scarlet-Violet-151-Elite-Trainer-Box", "external_id": ""},
        ],
    },
    {
        "name": "Pokemon 151 Ultra Premium Collection",
        "tcg": TCG.POKEMON,
        "category": Category.COLLECTION_BOX,
        "set_name": "Pokemon Card 151",
        "set_code": "SV3pt5",
        "release_date": "2023-10-06",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Pokemon-Boxes/Scarlet-Violet-151-Ultra-Premium-Collection", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0C7T4ZK1V", "external_id": "B0C7T4ZK1V"},
        ],
    },
    {
        "name": "Pokemon 151 Booster Bundle",
        "tcg": TCG.POKEMON,
        "category": Category.BUNDLE,
        "set_name": "Pokemon Card 151",
        "set_code": "SV3pt5",
        "release_date": "2023-09-22",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Pokemon-Boxes/Scarlet-Violet-151-Booster-Bundle", "external_id": ""},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Paradox-Rift-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CHY2JMM1", "external_id": "B0CHY2JMM1"},
        ],
    },

    # ==================== POKEMON TCG 2024 ====================
    {
        "name": "Paldean Fates Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Paldean Fates",
        "set_code": "SV4pt5",
        "release_date": "2024-01-26",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Paldean-Fates-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CN1FZK8V", "external_id": "B0CN1FZK8V"},
        ],
    },
    {
        "name": "Paldean Fates ETB",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Paldean Fates",
        "set_code": "SV4pt5",
        "release_date": "2024-01-26",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Elite-Trainer-Boxes/Scarlet-Violet-Paldean-Fates-Elite-Trainer-Box", "external_id": ""},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Temporal-Forces-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CQXR1TG7", "external_id": "B0CQXR1TG7"},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Twilight-Masquerade-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CXYMX5JH", "external_id": "B0CXYMX5JH"},
        ],
    },
    {
        "name": "Shrouded Fable Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Shrouded Fable",
        "set_code": "SV6pt5",
        "release_date": "2024-08-02",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Shrouded-Fable-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D5B8H7HN", "external_id": "B0D5B8H7HN"},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Stellar-Crown-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D5B6D3H8", "external_id": "B0D5B6D3H8"},
        ],
    },
    {
        "name": "Stellar Crown ETB",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Stellar Crown",
        "set_code": "SV7",
        "release_date": "2024-09-13",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Elite-Trainer-Boxes/Scarlet-Violet-Stellar-Crown-Elite-Trainer-Box", "external_id": ""},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Surging-Sparks-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DCSN6NTP", "external_id": "B0DCSN6NTP"},
        ],
    },
    {
        "name": "Surging Sparks ETB",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Surging Sparks",
        "set_code": "SV8",
        "release_date": "2024-11-08",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Elite-Trainer-Boxes/Scarlet-Violet-Surging-Sparks-Elite-Trainer-Box", "external_id": ""},
        ],
    },

    # ==================== POKEMON TCG 2025 ====================
    {
        "name": "Prismatic Evolutions Booster Box",
        "tcg": TCG.POKEMON,
        "category": Category.BOOSTER_BOX,
        "set_name": "Prismatic Evolutions",
        "set_code": "SV8pt5",
        "release_date": "2025-01-17",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Prismatic-Evolutions-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DLT36TM1", "external_id": "B0DLT36TM1"},
        ],
    },
    {
        "name": "Prismatic Evolutions ETB",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Prismatic Evolutions",
        "set_code": "SV8pt5",
        "release_date": "2025-01-17",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Elite-Trainer-Boxes/Scarlet-Violet-Prismatic-Evolutions-Elite-Trainer-Box", "external_id": ""},
        ],
    },
    {
        "name": "Prismatic Evolutions Ultra Premium Collection",
        "tcg": TCG.POKEMON,
        "category": Category.COLLECTION_BOX,
        "set_name": "Prismatic Evolutions",
        "set_code": "SV8pt5",
        "release_date": "2025-01-17",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Pokemon-Boxes/Scarlet-Violet-Prismatic-Evolutions-Ultra-Premium-Collection", "external_id": ""},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Journey-Together-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DR8BKWMQ", "external_id": "B0DR8BKWMQ"},
        ],
    },
    {
        "name": "Journey Together ETB",
        "tcg": TCG.POKEMON,
        "category": Category.ETB,
        "set_name": "Journey Together",
        "set_code": "SV9",
        "release_date": "2025-03-28",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Pokemon/Products/Elite-Trainer-Boxes/Scarlet-Violet-Journey-Together-Elite-Trainer-Box", "external_id": ""},
        ],
    },

    # ==================== MAGIC: THE GATHERING 2023 ====================
    {
        "name": "LotR: Tales of Middle-earth Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Lord of the Rings: Tales of Middle-earth",
        "set_code": "LTR",
        "release_date": "2023-06-23",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/The-Lord-of-the-Rings-Tales-of-Middle-earth-Draft-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0BTVRM77C", "external_id": "B0BTVRM77C"},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Wilds-of-Eldraine-Collector-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0C61GXVRS", "external_id": "B0C61GXVRS"},
        ],
    },
    {
        "name": "Lost Caverns of Ixalan Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "The Lost Caverns of Ixalan",
        "set_code": "LCI",
        "release_date": "2023-11-17",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/The-Lost-Caverns-of-Ixalan-Draft-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CHN3V5D4", "external_id": "B0CHN3V5D4"},
        ],
    },

    # ==================== MAGIC: THE GATHERING 2024 ====================
    {
        "name": "Murders at Karlov Manor Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Murders at Karlov Manor",
        "set_code": "MKM",
        "release_date": "2024-02-09",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Murders-at-Karlov-Manor-Play-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CN1G8Z6L", "external_id": "B0CN1G8Z6L"},
        ],
    },
    {
        "name": "Murders at Karlov Manor Bundle",
        "tcg": TCG.MAGIC,
        "category": Category.BUNDLE,
        "set_name": "Murders at Karlov Manor",
        "set_code": "MKM",
        "release_date": "2024-02-09",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Bundles/Murders-at-Karlov-Manor-Bundle", "external_id": ""},
        ],
    },
    {
        "name": "Outlaws of Thunder Junction Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Outlaws of Thunder Junction",
        "set_code": "OTJ",
        "release_date": "2024-04-19",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Outlaws-of-Thunder-Junction-Play-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0CXYN2RLX", "external_id": "B0CXYN2RLX"},
        ],
    },
    {
        "name": "Modern Horizons 3 Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Modern Horizons 3",
        "set_code": "MH3",
        "release_date": "2024-06-14",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Modern-Horizons-3-Play-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D1KBXWYQ", "external_id": "B0D1KBXWYQ"},
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
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Modern-Horizons-3-Collector-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D1KB7Y2T", "external_id": "B0D1KB7Y2T"},
        ],
    },
    {
        "name": "Bloomburrow Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Bloomburrow",
        "set_code": "BLB",
        "release_date": "2024-08-02",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Bloomburrow-Play-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D5B4CMZZ", "external_id": "B0D5B4CMZZ"},
        ],
    },
    {
        "name": "Duskmourn Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Duskmourn: House of Horror",
        "set_code": "DSK",
        "release_date": "2024-09-27",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Duskmourn-House-of-Horror-Play-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0D9V4RLCL", "external_id": "B0D9V4RLCL"},
        ],
    },
    {
        "name": "Foundations Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Foundations",
        "set_code": "FDN",
        "release_date": "2024-11-15",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Foundations-Play-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DCSN9VQP", "external_id": "B0DCSN9VQP"},
        ],
    },
    {
        "name": "Foundations Collector Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Foundations",
        "set_code": "FDN",
        "release_date": "2024-11-15",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Foundations-Collector-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DCSMVPFB", "external_id": "B0DCSMVPFB"},
        ],
    },

    # ==================== MAGIC: THE GATHERING 2025 ====================
    {
        "name": "Aetherdrift Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Aetherdrift",
        "set_code": "DFT",
        "release_date": "2025-02-14",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Aetherdrift-Play-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DLT31QDX", "external_id": "B0DLT31QDX"},
        ],
    },
    {
        "name": "Tarkir: Dragonstorm Draft Booster Box",
        "tcg": TCG.MAGIC,
        "category": Category.BOOSTER_BOX,
        "set_name": "Tarkir: Dragonstorm",
        "set_code": "TDM",
        "release_date": "2025-04-11",
        "links": [
            {"marketplace": Marketplace.CARDMARKET, "url": "https://www.cardmarket.com/en/Magic/Products/Booster-Boxes/Tarkir-Dragonstorm-Play-Booster-Box", "external_id": ""},
            {"marketplace": Marketplace.AMAZON, "url": "https://www.amazon.de/dp/B0DR8B1TDP", "external_id": "B0DR8B1TDP"},
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
