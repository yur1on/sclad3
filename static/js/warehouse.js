// Переменная для хранения направлений сортировки для каждого столбца
let sortDirections = {};

// Функция сортировки таблицы
function sortTable(columnIndex) {
    const table = document.getElementById("parts-table");
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.querySelectorAll("tr"));

    if (!sortDirections[columnIndex]) {
        sortDirections[columnIndex] = 'asc';
    } else {
        sortDirections[columnIndex] = sortDirections[columnIndex] === 'asc' ? 'desc' : 'asc';
    }

    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim().toLowerCase();
        const bText = b.cells[columnIndex].textContent.trim().toLowerCase();
        return (aText < bText ? -1 : aText > bText ? 1 : 0) * (sortDirections[columnIndex] === 'asc' ? 1 : -1);
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    updateSortIndicators(columnIndex);
}

// Обновление индикаторов сортировки
function updateSortIndicators(activeColumnIndex) {
    const headers = document.querySelectorAll("#parts-table thead th");
    headers.forEach((th, index) => {
        th.innerHTML = th.textContent.replace(' ▲', '').replace(' ▼', '');
        if (index === activeColumnIndex) {
            th.innerHTML += sortDirections[activeColumnIndex] === 'asc' ? ' ▲' : ' ▼';
        }
    });
}

// Связь между устройствами, брендами и моделями
const deviceBrandModelMap = {
    'Телефон': {
        'Samsung': ['a10', 'a20', 'a30', 's10'],
        'Huawei': ['p10', 'p20', 'honor 50'],
        'Xiaomi': ['redmi 5', 'redmi 6', 'redmi 7'],
        'Realme': ['realme 8', 'realme 6', 'realme 7', 'realme x2'],
        'LG': ['LG G7', 'LG V40', 'LG K50']
    },
    'Планшет': {
        'Samsung': ['tab s3', 'tab s4', 'tab a'],
        'Huawei': ['mediapad t5', 'mediapad m5'],
        'Xiaomi': ['mi pad 4', 'mi pad 5'],
        'Apple': ['iPad Air', 'iPad Pro', 'iPad Mini']
    },
    'Ноутбук': {
        'Dell': ['XPS 13', 'XPS 15', 'Inspiron'],
        'HP': ['Spectre x360', 'Envy 13', 'Pavilion 15'],
        'Lenovo': ['ThinkPad X1', 'Yoga C930', 'Legion Y540'],
        'Asus': ['ZenBook', 'ROG Strix', 'VivoBook']
    },
    'Смарт-часы': {
        'Apple': ['Series 3', 'Series 4', 'Series 5'],
        'Samsung': ['Galaxy Watch', 'Galaxy Watch Active', 'Gear S3'],
        'Xiaomi': ['Amazfit', 'Mi Band 4', 'Mi Band 5']
    }
};

// Функция для отображения кнопок устройств
document.getElementById("show-devices-btn").addEventListener("click", function() {
    const deviceButtonsContainer = document.getElementById("device-buttons-container");
    deviceButtonsContainer.style.display = "block";
    this.style.display = "none";
    document.getElementById("back-btn").style.display = "inline-block";

    const deviceButtons = document.getElementById("device-buttons");
    deviceButtons.innerHTML = '';

    Object.keys(deviceBrandModelMap).forEach(device => {
        const button = document.createElement("button");
        button.textContent = device;
        button.className = "btn btn-outline-primary me-2 mb-2 device-btn";
        button.addEventListener("click", () => showBrandButtons(device));
        deviceButtons.appendChild(button);
    });
});

// Функция для отображения кнопок брендов
function showBrandButtons(device) {
    const brandButtonsContainer = document.getElementById("brand-buttons");
    brandButtonsContainer.innerHTML = '';
    const brands = deviceBrandModelMap[device];

    Object.keys(brands).forEach(brand => {
        const button = document.createElement("button");
        button.textContent = brand;
        button.className = "btn btn-outline-primary me-2 mb-2 brand-btn";
        button.addEventListener("click", () => showPartsTable(device, brand));
        brandButtonsContainer.appendChild(button);
    });

    // Подсветить выбранное устройство
    highlightSelectedButton('.device-btn', device);
}

// Функция для подсветки выбранной кнопки
function highlightSelectedButton(selector, text) {
    const buttons = document.querySelectorAll(selector);
    buttons.forEach(button => {
        if (button.textContent === text) {
            button.classList.add('btn-primary');
            button.classList.remove('btn-outline-primary');
        } else {
            button.classList.add('btn-outline-primary');
            button.classList.remove('btn-primary');
        }
    });
}

// Функция для отображения таблицы с запчастями для выбранных устройства и бренда
function showPartsTable(device, brand) {
    const partsTableContainer = document.getElementById("parts-table-container");
    const rows = partsTableContainer.querySelectorAll("tbody tr");

    rows.forEach(row => {
        const deviceCell = row.cells[0].textContent.trim();
        const brandCell = row.cells[1].textContent.trim();
        if (deviceCell === device && brandCell === brand) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });

    // Подсветить выбранный бренд
    highlightSelectedButton('.brand-btn', brand);
}

// Функция для возврата к выбору устройств
document.getElementById("back-btn").addEventListener("click", function() {
    document.getElementById("device-buttons-container").style.display = "none";
    document.getElementById("show-devices-btn").style.display = "inline-block";
    this.style.display = "none";
});