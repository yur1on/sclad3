// Функция для обработки изменения устройства
function handleDeviceChange() {
    resetBrandModelAndPartType();

    // Обновить список брендов в зависимости от выбранного устройства
    updateBrandOptions();
}

// Сброс значений полей "Бренд", "Модель" и "Тип запчасти"
function resetBrandModelAndPartType() {
    document.getElementById('id_brand').value = '';
    document.getElementById('id_model').value = '';
    document.getElementById('id_part_type').value = '';

    // Очистить списки datalist для "Бренд", "Модель"
    document.getElementById('brands').innerHTML = '';
    document.getElementById('models').innerHTML = '';
}

// Функция для обновления списка брендов
function updateBrandOptions() {
    var device = document.getElementById('id_device').value;
    var brandSelect = document.getElementById('brands');
    brandSelect.innerHTML = '';  // Очистить предыдущие бренды

    var brands = {
        'Телефон': ['Samsung', 'Huawei', 'Xiaomi', 'Apple', 'LG'],
        'Планшет': ['Samsung', 'Huawei'],
        'Ноутбук': ['Asus', 'Acer'],
        'Компьютер': ['Dell', 'HP', 'Lenovo'],
        'Смарт-часы': ['Apple', 'Samsung', 'Garmin']
    };

    if (brands[device]) {
        brands[device].forEach(function(brand) {
            var option = document.createElement('option');
            option.value = brand;
            option.text = brand;
            brandSelect.appendChild(option);
        });
    }

    // Обновить список моделей после выбора бренда
    updateModelOptions();
}

// Функция для обновления списка моделей
function updateModelOptions() {
    var device = document.getElementById('id_device').value;
    var brand = document.getElementById('id_brand').value;
    var modelSelect = document.getElementById('models');
    modelSelect.innerHTML = '';  // Очистить предыдущие модели

    var models = {
        'Телефон': {
            'Samsung': ['A01', 'A02', 'A03'],
            'Huawei': ['P40', 'P50'],
            'Xiaomi': ['Redmi Note 10', 'Redmi Note 9']
        },
        'Планшет': {
            'Samsung': ['T500', 'T735'],
            'Huawei': ['MatePad 10.4']
        },
        'Ноутбук': {
            'Asus': ['ZenBook 14'],
            'Acer': ['Aspire 7']
        },
        'Компьютер': {
            'Dell': ['Inspiron 15'],
            'HP': ['Pavilion 15'],
            'Lenovo': ['ThinkPad X1']
        },
        'Смарт-часы': {
            'Apple': ['Apple Watch Series 8'],
            'Samsung': ['Galaxy Watch 5'],
            'Garmin': ['Fenix 7']
        }
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

// Обработчик изменения типа запчасти (если требуется)
function updatePartTypeOptions() {
    var device = document.getElementById('id_device').value;
    var partTypeSelect = document.getElementById('part_types');
    partTypeSelect.innerHTML = '';  // Очистить предыдущие типы запчастей

    var partTypes = {
        'Телефон': ['Дисплей', 'Батарея'],
        'Планшет': ['Дисплей', 'Задняя крышка'],
        'Ноутбук': ['Клавиатура', 'Дисплей'],
        'Компьютер': ['Процессор', 'Материнская плата'],
        'Смарт-часы': ['Дисплей', 'Батарея']
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
