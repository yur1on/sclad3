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
