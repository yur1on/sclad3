const deviceBrandMap = {
    'Телефон': ['Samsung', 'Huawei', 'Xiaomi', 'Apple', 'LG'],
    'Планшет': ['Samsung', 'Huawei'],
    'Ноутбук': ['Asus', 'Acer'],
    'Смарт-часы': ['Apple', 'Samsung', 'Garmin', 'Huawei']
};

const brandModelMap = {
    'Телефон': {
        'Samsung': ['S21', 'A10', 'A20', 'A30'],
        'Huawei': ['P40', 'P50'],
        'Xiaomi': ['Redmi Note 10', 'Mi 11'],
        'Apple': ['iPhone 13', 'iPhone 12'],
        'LG': ['LG G7', 'LG K50']
    },
    'Планшет': {
        'Samsung': ['T500', 'T735'],
        'Huawei': ['MatePad 10.4']
    },
    'Ноутбук': {
        'Asus': ['ZenBook 14', 'ROG Strix G15'],
        'Acer': ['Aspire 7', 'Nitro 5']
    },
    'Смарт-часы': {
        'Apple': ['Apple Watch Series 8', 'Apple Watch SE'],
        'Samsung': ['Galaxy Watch 5', 'Galaxy Watch Active 2'],
        'Garmin': ['Forerunner 945', 'Fenix 7']
    }
};

const modelPartTypeMap = {
    'S21': ['Дисплей', 'Камера', 'Батарея'],
    'A10': ['Дисплей', 'Камера', 'Батарея'],
    'P40': ['Дисплей', 'Камера'],
    'Redmi Note 10': ['Дисплей', 'Камера'],
    'iPhone 13': ['Дисплей', 'Камера'],
};

document.getElementById('device').addEventListener('input', function() {
    const device = this.value;
    const brandInput = document.getElementById('brand');
    const modelInput = document.getElementById('model');
    const partTypeInput = document.getElementById('part_type');

    brandInput.value = '';
    modelInput.value = '';
    partTypeInput.value = '';
    document.getElementById('brand-list').innerHTML = '';
    document.getElementById('model-list').innerHTML = '';
    document.getElementById('part-type-list').innerHTML = '';

    if (deviceBrandMap[device]) {
        const brandOptions = deviceBrandMap[device].map(brand => `<option value="${brand}">`).join('');
        document.getElementById('brand-list').innerHTML = brandOptions;
    }
});

// Обработчики событий для брендов и моделей...
document.addEventListener('DOMContentLoaded', function () {
    const regionSelect = document.getElementById('id_region');
    const citySelect = document.getElementById('id_city');

    const citiesByRegion = {
        'Минская область': [
              'Минск','Березино','Бобр','Борисов','Боровляны','Вилейка','Воложин','Городея','Дзержинск','Дружный',
              'Жодино','Заславль','Ивенец','Клецк','Копыль','Кривичи','Крупки',
              'Логойск','Любань','Марьина Горка','Молодечно','Мядель','Негорелое','Несвиж','Плещеницы',
              'Радошковичи','Руденск','Свирь','Слуцк','Смиловичи','Смолевичи','Солигорск','Старобин','Старые Дороги',
              'Столбцы','Узда','Уречье','Холопеничи','Червень'

        ],

        'Гомельская область': ['Гомель','Брагин','Буда-Кошелёво','Василевичи','Ветка','Добруш','Ельск',
               'Житковичи','Жлобин','Калинковичи','Корма','Лельчицы','Лоев','Мозырь','Наровля','Озаричи','Октябрьский',
               'Петриков','Речица','Рогачёв','Светлогорск','Стрешин','Туров',
               'Хойники','Чечерск'
    ],

        'Гродненская область': [
                'Гродно','Большая Берестовица','Волковыск','Вороново','Дятлово','Зельва',
                'Ивье','Козловщина','Кореличи','Лида','Любча','Мир','Мосты','Новогрудок','Островец','Ошмяны',
                'Свислочь','Скидель','Слоним', 'Сморгонь','Сопоцкин','Щучин'
    ],

        'Витебская область': [
              'Витебск','Бегомль','Бешенковичи','Браслав','Верхнедвинск','Видзы','Глубокое','Городок','Дисна','Докшицы',
              'Друя','Дубровно','Езерище','Лепель','Лиозно','Миоры','Новолукомль','Новополоцк','Орша',
              'Полоцк','Поставы','Россоны','Сенно','Толочин',
              'Шарковщина', 'Тарчин','Ушачи','Чашники','Шарковщина','Шумилино'
    ],
        'Брестская область': [
               'Брест', "Антополь", 'Барановичи', 'Белоозёрск', 'Берёза', 'Высокое', 'Ганцевичи', 'Городище',
               'Давид-Городок', 'Дрогичин', 'Жабинка', 'Иваново', 'Ивацевичи', 'Каменец', 'Кобрин', 'Коссово',
               'Логишин', 'Лунинец', 'Ляховичи', 'Малорита', 'Пинск', 'Пружаны', 'Ружаны', 'Столин', 'Телеханы',
               'Шерешёво'
    ],

        'Могилёвская область': [
               'Могилёв','Белыничи','Бобруйск','Быхов','Глуск','Горки','Дрибин','Кировск',
               'Климовичи','Кличев','Костюковичи','Краснополье','Кричев','Круглое','Мстиславль',
               'Осиповичи','Славгород','Хотимск','Чаусы','Чериков','Шклов'
    ]
    };

    regionSelect.addEventListener('change', function () {
        const selectedRegion = regionSelect.value;
        citySelect.innerHTML = '';  // Очищаем предыдущие города

        if (citiesByRegion[selectedRegion]) {
            citiesByRegion[selectedRegion].forEach(function (city) {
                const option = document.createElement('option');
                option.value = city;
                option.text = city;
                citySelect.appendChild(option);
            });
        } else {
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.text = 'Выберите город';
            citySelect.appendChild(defaultOption);
        }
    });
});
