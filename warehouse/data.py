
CONDITIONS = ["новый", "б/у", "оригинал"]

DATA = {
    "Телефон": {
        "brands": ["Apple", "Samsung", "Huawei", "Honor", "Xiaomi", "Poco", "Realme", "Vivo", "Tecno", "Infinix", "TCL",
                   "Oppo", "Google", "OnePlus", "Alcatel", "Amigoo", "Archos", "Asus", "Black Shark",
                   "BlackBerry", "Blackview", "BLU", "Cat", "Caterpillar", "Coolpad", "Cubot", "Doogee",
                   "Elephone", "HTC", "Lava", "Lenovo", "LG", "Meizu", "Micromax", "Motorola", "Nokia",
                   "Nubia", "Oukitel", "Sharp", "Sony", "Wiko", "ZTE", ],

        "models": {
            "Apple": ["iPhone 16 Pro Max", "iPhone 16 Pro", "iPhone 16 Plus", "iPhone 16", "iPhone 15 Pro Max", "iPhone 15 Pro",
                      "iPhone 15 Plus", "iPhone 15", "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14 Plus", "iPhone 14", "iPhone SE 2022",
                      "iPhone 13 Pro Max", "iPhone 13 Pro", "iPhone 13", "iPhone 13 mini", "iPhone 12 Pro Max", "iPhone 12 Pro", "iPhone 12",
                      "iPhone 12 mini", "iPhone SE 2020", "iPhone 11 Pro Max", "iPhone 11 Pro", "iPhone 11", "iPhone Xr", "iPhone Xs Max", "iPhone Xs",
                      "iPhone X", "iPhone 8 Plus", "iPhone 8", "iPhone 7 Plus", "iPhone 7", "iPhone SE", "iPhone 6s Plus", "iPhone 6s", "iPhone 6 Plus",
                      "iPhone 6", "iPhone 5s", "iPhone 5c", "iPhone 5"],
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
