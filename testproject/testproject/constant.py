class CONFIG:
    FIXPRICE_CARD = True  # при true скидки на fix_price будут считаться при false- скидки при условии наличия карты фикспрайса считаться не будут

class FIELDS:

    TIMESTAMP = "timestamp"
    RPC = "RPC"
    URL = "url"
    TITLE = "title"
    MARKETING_TAGS = "marketing_tags"
    BRAND = "brand"
    SECTION = "section"
    PRICE_DATA = "price_data"
    STOCK = "stock"
    ASSETS = "assets"
    METADATA = "metadata"
    VARIANTS = "variants"


class PRICE_DATA:
    CURRENT = "current"
    ORIGINAL = "original"
    SALE_TAG = "sale_tag"


class STOCK:
    IN_STOCK = "in_stock"
    COUNT = "count"


class ASSETS:
    MAIN_IMAGE = "main_image"
    SET_IMAGE = "set_images"
    VIEW360 = "view360"
    VIDEO = "video"


class METADATA:
    DESCRIPTION = "__description"


class COMMON:
    FIELD_NOT_SET = None
    UNITS_OF_VOLUME = [' л,', ' мл,', ' мл']