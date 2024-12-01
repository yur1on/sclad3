document.addEventListener('DOMContentLoaded', function() {
    const deviceInput = document.getElementById('device');
    const brandInput = document.getElementById('brand');
    const modelInput = document.getElementById('model');
    const partTypeInput = document.getElementById('part_type');

    deviceInput.addEventListener('input', function() {
        fetch(`/get_dynamic_data?device=${deviceInput.value}`)
            .then(response => response.json())
            .then(data => {
                updateDatalist('brand-list', data.brands);
                updateDatalist('part-type-list', data.part_types);
                clearDatalist('model-list'); // Очистка моделей
                brandInput.value = '';       // Очистка текущего бренда
                modelInput.value = '';       // Очистка текущей модели
                partTypeInput.value = '';    // Очистка текущего типа запчасти
            });
    });

    brandInput.addEventListener('input', function() {
        fetch(`/get_dynamic_data?device=${deviceInput.value}&brand=${brandInput.value}`)
            .then(response => response.json())
            .then(data => {
                updateDatalist('model-list', data.models);
                modelInput.value = ''; // Очистка текущей модели
            });
    });

    partTypeInput.addEventListener('input', function() {
        fetch(`/get_dynamic_data?device=${deviceInput.value}&part_type=${partTypeInput.value}`)
            .then(response => response.json())
            .then(data => {
                updateDatalist('part-type-list', data.colors);
            });
    });

    function updateDatalist(id, options) {
        const datalist = document.getElementById(id);
        datalist.innerHTML = options.map(option => `<option value="${option}">`).join('');
    }

    function clearDatalist(id) {
        const datalist = document.getElementById(id);
        datalist.innerHTML = '';
    }
});





// Работа с регионами и городами
document.addEventListener('DOMContentLoaded', function() {
    // Поля простого поиска
    const regionSelect = document.getElementById('id_region');
    const citySelect = document.getElementById('id_city');

    // Поля расширенного поиска
    const regionAdvSelect = document.getElementById('id_region_adv');
    const cityAdvSelect = document.getElementById('id_city_adv');

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
    // Функция для заполнения списка городов
    function updateCitySelect(regionSelect, citySelect) {
        const selectedRegion = regionSelect.value;
        citySelect.innerHTML = '';

        if (citiesByRegion[selectedRegion]) {
            citiesByRegion[selectedRegion].forEach(function(city) {
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
    }

    // Слушатели событий для простого поиска
    regionSelect.addEventListener('change', function() {
        updateCitySelect(regionSelect, citySelect);
    });

    // Слушатели событий для расширенного поиска
    regionAdvSelect.addEventListener('change', function() {
        updateCitySelect(regionAdvSelect, cityAdvSelect);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('toggle-advanced-search');
    const basicSearch = document.getElementById('basic-search');
    const advancedSearch = document.getElementById('advanced-search');

    toggleButton.addEventListener('click', function () {
        if (basicSearch.style.display === 'none') {
            basicSearch.style.display = 'block';
            advancedSearch.style.display = 'none';
            toggleButton.textContent = 'Расширенный поиск';
        } else {
            basicSearch.style.display = 'none';
            advancedSearch.style.display = 'block';
            toggleButton.textContent = 'Обычный поиск';
        }
    });
});