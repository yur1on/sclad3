
CONDITIONS = ["новый", "б/у", "оригинал"]

DATA = {
    "Телефон": {
        "brands": ["Apple", "Samsung", "Huawei", "Honor", "Xiaomi", "Poco", "Realme", "Vivo", "Tecno", "Infinix", "TCL",
                   "Oppo", "Google", "OnePlus", "Alcatel", "Amigoo", "Archos", "Asus", "Black Shark",
                   "BlackBerry", "Blackview", "BLU", "Cat", "Caterpillar", "Coolpad", "Cubot", "Doogee",
                   "Elephone", "HTC", "Lava", "Lenovo", "LG", "Meizu", "Micromax", "Motorola", "Nokia",
                   "Nubia", "Oukitel", "Sharp", "Sony", "Wiko", "ZTE",  ],

        "models": {
            "Samsung": ["A01", "A02", "A11", "A12", "A20", "A30"],
            "Huawei": ["P40", "P40 Lite", "P50"],
        },

        "part_types": ["Аккумулятор", "Динамик", "Дисплей"],

        "colors": {
            "Дисплей": ["Черный", "Белый", "Серый"],
            "Аккумулятор": ["Черный", "Белый"],
        },

        # Все типы запчастей будут использовать общий перечень состояний
        "conditions": CONDITIONS,
    },



    "Планшет": {
        "brands": ["Apple", "Samsung", "Huawei", "Honor", "Xiaomi", "Poco", "Realme", "Lenovo", "Vivo", "Infinix", "TCL"
                   "AGM", "Alcatel", "Blackview", "Chuwi", "Cubot", "Doogee", "Fossibot", "Google", "Hotwav", "HTC",
                   "Microsoft", "Motorola", "Nokia", "Nubia", "OnePlus", "Oppo", "Oukitel", "Teclast", "Ulefone", "UMiDIGI",
                   "ZTE"],

        "models": {
            "Samsung": ["1", "2", "91", "12", "20", "30"],
            "Huawei": ["P40", "P40 Lite", "P50"],
        },

        "part_types": ["Аккумулятор", "Динамик", "Дисплей", "Задняя крышка"],

        "colors": {
            "Дисплей": ["Черный", "Белый", "Серый"],
            "Аккумулятор": ["Черный", "Белый"],
            "Задняя крышка": ["Черный", "Белый"],
        },
        # Все типы запчастей будут использовать общий перечень состояний
        "conditions": CONDITIONS,
    },


    "Смарт-часы": {
        "brands": ["Samsung", "Huawei", "Xiaomi", "Apple", "LG", "Realme"],

        "models": {
            "Samsung": ["1", "2", "91", "12", "20", "30"],
            "Huawei": ["P40", "P40 Lite", "P50"],
        },

        "part_types": ["Аккумулятор", "Динамик", "Дисплей", "Задняя крышка"],

        "colors": {
            "Дисплей": ["Черный", "Белый", "Серый"],
            "Аккумулятор": ["Черный", "Белый"],
            "Задняя крышка": ["Черный", "Белый"],
        },
        # Все типы запчастей будут использовать общий перечень состояний
        "conditions": CONDITIONS,
    },


    "Ноутбук": {
        "brands": ["Samsung", "Huawei", "Xiaomi", "Apple", "LG", "Realme"],

        "models": {
            "Samsung": ["1", "2", "91", "12", "20", "30"],
            "Huawei": ["P40", "P40 Lite", "P50"],
        },

        "part_types": ["Аккумулятор", "Динамик", "Дисплей", "Задняя крышка"],

        "colors": {
            "Дисплей": ["Черный", "Белый", "Серый"],
            "Аккумулятор": ["Черный", "Белый"],
            "Задняя крышка": ["Черный", "Белый"],
        },
        # Все типы запчастей будут использовать общий перечень состояний
        "conditions": CONDITIONS,
    }
}
