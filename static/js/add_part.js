 function handleDeviceChange() {
            // Сбросить значения в полях "Бренд", "Модель" и "Тип запчасти"
            resetBrandModelAndPartType();
            // Обновить списки брендов, моделей и типов запчастей
            updateBrandOptions();
        }
        function resetBrandModelAndPartType() {
            document.getElementById('id_brand').value = '';
            document.getElementById('id_model').value = '';
            document.getElementById('id_part_type').value = '';
            document.getElementById('id_color').value = '';
            // Очистить списки datalist для "Бренд", "Модель" и "Тип запчасти"
            document.getElementById('brands').innerHTML = '';
            document.getElementById('models').innerHTML = '';
            document.getElementById('part_types').innerHTML = '';
            document.getElementById('colors').innerHTML = '';
        }
        function updateBrandOptions() {
            var device = document.getElementById('id_device').value;
            var brandSelect = document.getElementById('brands');
            brandSelect.innerHTML = '';  // Очистить предыдущие бренды
            var brands = {
                'Телефон': ['Samsung', 'Huawei', 'Xiaomi', 'Apple', 'LG', 'Realme'],
                'Планшет': ['Samsung', 'Huawei'],
                'Ноутбук': ['Asus', 'Acer'],
                'Компьютер': ['Dell', 'HP', 'Lenovo'],
                'Смарт-часы': ['Apple', 'Samsung', 'Garmin', 'Huawei']
                // Добавьте другие устройства и бренды по мере необходимости
            };
            if (brands[device]) {
                brands[device].forEach(function(brand) {
                    var option = document.createElement('option');
                    option.value = brand;
                    option.text = brand;
                    brandSelect.appendChild(option);
                });
            }
            // После обновления брендов, нужно обновить типы запчастей
            updatePartTypeOptions();
        }
        function updateModelOptions() {
            var device = document.getElementById('id_device').value;
            var brand = document.getElementById('id_brand').value;
            var modelSelect = document.getElementById('models');
            modelSelect.innerHTML = '';  // Очистить предыдущие модели
            var models = {
                'Телефон': {
                    'Samsung': ['A01', 'A01 Core', 'A02', 'A02s', 'A03', 'A03s', 'A03 Core', 'A8s', 'A10', 'A10s', 'A11', 'A12', 'A13', 'A14', 'A15', 'A11', 'A12', 'A13', 'A14', 'A20', 'A20s', 'A21s', 'A22 5G', 'A30', 'A30s', 'A31', 'A40', 'A41', 'A50', 'A51', 'A52 5G','A52s 5G','A60','A70','A71','A72','A80','A80s'],
                    'Huawei': ['P40', 'P40 Lite', 'P50'],
                    'Xiaomi': ['Redmi Note 10', 'Redmi Note 9', 'Mi 11'],
                    'Apple': ['iPhone 13', 'iPhone 12', 'iPhone 11'],
                    'LG': ['LG G7', 'LG V40', 'LG K50'],
                    'Realme': ['realme 5', 'realme 6', 'realme 7', 'realme x2']
                },
                'Планшет': {
                    'Samsung': ['T500', 'T735'],
                    'Huawei': ['MatePad 10.4', 'Pad 8']
                },
                'Ноутбук': {
                    'Asus': ['ZenBook 14', 'ROG Strix G15', 'VivoBook S15'],
                    'Acer': ['Aspire 7', 'Nitro 5', 'Swift 3']
                },
                'Компьютер': {
                    'Dell': ['Inspiron 15', 'XPS 13', 'Alienware m15'],
                    'HP': ['Pavilion 15', 'Spectre x360', 'Omen 17'],
                    'Lenovo': ['ThinkPad X1', 'Legion 5', 'Yoga 7']
                },
                'Смарт-часы': {
                    'Apple': ['Apple Watch Series 8', 'Apple Watch SE', 'Apple Watch Ultra'],
                    'Samsung': ['Galaxy Watch 5', 'Galaxy Watch 4', 'Galaxy Watch Active 2'],
                    'Garmin': ['Forerunner 945', 'Fenix 7', 'Venu 2'],
                    'Huawei': ['Watch GT 3', 'Watch Fit', 'Watch 3']
                }
                // Добавьте другие бренды и модели по мере необходимости
            };
            if (device in models && brand in models[device]) {
                models[device][brand].forEach(function(model) {
                    var option = document.createElement('option');
                    option.value = model;
                    option.text = model;
                    modelSelect.appendChild(option);
                });
            }
        }
        function updatePartTypeOptions() {
            var device = document.getElementById('id_device').value;
            var partTypeSelect = document.getElementById('part_types');
            partTypeSelect.innerHTML = '';  // Очистить предыдущие типы запчастей
            var partTypes = {
                'Телефон': ['Аккумулятор','Динамик', 'Дисплей', 'Задняя крышка', 'Камера основная', 'Камера фронтальная', 'Коннектор', 'Коннектор SIM', 'Коннектор АКБ', 'Коннектор LCD', 'Микрофон', 'Разьем зарядки', 'Рамка дисплея', 'Стекло для переклейки', 'Стекло камеры', 'Системная плата','Суб плата', 'Шлейф боковых кнопок', 'Шлейф дисплея', 'Шлейф межплатный', 'Шлейф с отпечатком пальца',],
                'Планшет': ['Динамик', 'Дисплей', 'Шлейф межплатный', 'Основная плата', 'Стекло для переклейки', 'Задняя крышка'],
                'Ноутбук': ['Динамик', 'Дисплей', 'Клавиатура', 'Батарея', 'Жесткий диск', 'Оперативная память'],
                'Компьютер': ['Процессор', 'Материнская плата', 'Блок питания', 'Оперативная память', 'Жесткий диск', 'Корпус'],
                'Смарт-часы': ['Динамик', 'Дисплей', 'Батарея', 'Шлейф межплатный', 'Корпус', 'Сенсор']
            };
            if (partTypes[device]) {
                partTypes[device].forEach(function(partType) {
                    var option = document.createElement('option');
                    option.value = partType;
                    option.text = partType;
                    partTypeSelect.appendChild(option);
                });
            }
        }
        function handlePartTypeChange() {
            var partType = document.getElementById('id_part_type').value;
            var colorGroup = document.getElementById('color-group');
            var colorSelect = document.getElementById('colors');
            colorSelect.innerHTML = '';  // Очистить предыдущие цвета
            var colors = {
                'Дисплей': ['Черный', 'Белый', 'Серый', 'Синий'],
                'Задняя крышка': ['Черный', 'Белый', 'Красный', 'Зеленый'],
                'Шлейф с отпечатком пальца': ['Черный', 'Белый', 'Серый', 'Синий', 'Золото'],
            };
            if (colors[partType]) {
                colorGroup.style.display = 'block'; // Показать поле выбора цвета
                colors[partType].forEach(function(color) {
                    var option = document.createElement('option');
                    option.value = color;
                    option.text = color;
                    colorSelect.appendChild(option);
                });
            } else {
                colorGroup.style.display = 'none'; // Скрыть поле выбора цвета
            }
        }