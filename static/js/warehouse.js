document.addEventListener('DOMContentLoaded', function() {
    const deviceInput = document.getElementById('device');
    const brandInput = document.getElementById('brand');
    const modelInput = document.getElementById('model');

    deviceInput.addEventListener('input', function() {
        const selectedDevice = deviceInput.value;
        brandInput.value = '';
        modelInput.value = '';
        clearDatalist('brands');
        clearDatalist('models');

        if (selectedDevice) {
            fetch(`/get-brands/?device=${selectedDevice}`)
                .then(response => response.json())
                .then(data => {
                    populateDatalist('brands', data.brands);
                });
        }
    });

    brandInput.addEventListener('input', function() {
        const selectedBrand = brandInput.value;
        const selectedDevice = deviceInput.value;  // Устройство тоже должно быть учтено

        modelInput.value = '';
        clearDatalist('models');

        if (selectedBrand) {
            fetch(`/get-models/?brand=${selectedBrand}&device=${selectedDevice}`)  // Отправляем и устройство, и бренд
                .then(response => response.json())
                .then(data => {
                    populateDatalist('models', data.models);
                });
        }
    });

    function populateDatalist(id, items) {
        const datalist = document.getElementById(id);
        datalist.innerHTML = '';
        items.forEach(function(item) {
            const option = document.createElement('option');
            option.value = item;
            datalist.appendChild(option);
        });
    }

    function clearDatalist(id) {
        const datalist = document.getElementById(id);
        datalist.innerHTML = '';
    }
});
document.addEventListener('DOMContentLoaded', function() {
    const deviceButtonsContainer = document.getElementById('device-buttons-container');
    const brandButtonsContainer = document.getElementById('brand-buttons-container');
    const modelButtonsContainer = document.getElementById('model-buttons-container');
    const partTypeButtonsContainer = document.getElementById('part-type-buttons-container');

    const deviceButtons = document.getElementById('device-buttons');
    const brandButtons = document.getElementById('brand-buttons');
    const modelButtons = document.getElementById('model-buttons');
    const partTypeButtons = document.getElementById('part-type-buttons');

    let selectedDevice = '';  // Для хранения выбранного устройства
    let selectedBrand = '';   // Для хранения выбранного бренда
    let selectedModel = '';   // Для хранения выбранной модели

    // Загрузка кнопок для устройств при загрузке страницы
    fetch('/get-devices/')
        .then(response => response.json())
        .then(data => {
            populateButtons(deviceButtons, data.devices, handleDeviceClick);
        });

    // Обработка нажатия на устройство
    function handleDeviceClick(device) {
        selectedDevice = device;  // Сохраняем выбранное устройство
        brandButtons.innerHTML = '';  // Очищаем старые кнопки брендов
        modelButtonsContainer.style.display = 'none';
        partTypeButtonsContainer.style.display = 'none';

        fetch(`/get-brands/?device=${device}`)  // Передаем устройство в запрос
            .then(response => response.json())
            .then(data => {
                brandButtonsContainer.style.display = 'block';
                populateButtons(brandButtons, data.brands, handleBrandClick);
            });
    }

    // Обработка нажатия на бренд
    function handleBrandClick(brand) {
        selectedBrand = brand;  // Сохраняем выбранный бренд
        modelButtons.innerHTML = '';  // Очищаем старые кнопки моделей

        fetch(`/get-models/?device=${selectedDevice}&brand=${brand}`)  // Учитываем и устройство, и бренд
            .then(response => response.json())
            .then(data => {
                modelButtonsContainer.style.display = 'block';
                populateButtons(modelButtons, data.models, handleModelClick);
            });
    }

    // Обработка нажатия на модель
    function handleModelClick(model) {
        selectedModel = model;  // Сохраняем выбранную модель
        partTypeButtons.innerHTML = '';  // Очищаем старые кнопки типов запчастей

        // Передаем устройство, бренд и модель в запрос для получения типов запчастей
        fetch(`/get-part-types/?device=${selectedDevice}&brand=${selectedBrand}&model=${model}`)
            .then(response => response.json())
            .then(data => {
                partTypeButtonsContainer.style.display = 'block';
                populateButtons(partTypeButtons, data.part_types, handlePartTypeClick);
            });
    }

    // Обработка нажатия на тип запчасти
    function handlePartTypeClick(partType) {
        // Отправляем запрос для получения запчастей по устройству, модели, бренду и типу запчасти
        fetch(`/get-parts/?device=${selectedDevice}&brand=${selectedBrand}&model=${selectedModel}&part_type=${partType}`)
            .then(response => response.json())
            .then(data => {
                // Функция для отображения запчастей в таблице
                displayParts(data.parts);
            });
    }

    // Функция для отображения кнопок
    function populateButtons(container, items, clickHandler) {
        container.innerHTML = '';  // Очищаем контейнер от старых кнопок
        items.forEach(item => {
            const button = document.createElement('button');
            button.classList.add('btn', 'btn-primary', 'me-2', 'mb-2');
            button.textContent = item;
            button.addEventListener('click', () => clickHandler(item));
            container.appendChild(button);
        });
    }

    // Функция для отображения запчастей в таблице
    function displayParts(parts) {
        const tbody = document.querySelector('#parts-table tbody');
        tbody.innerHTML = '';  // Очищаем старые данные

        parts.forEach(part => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${part.device}</td>
                <td>${part.brand}</td>
                <td>${part.model}</td>
                <td>${part.part_type}</td>
                <td>${part.color || 'Не указан'}</td>
                <td>${part.quantity}</td>
                <td>${part.price}</td>
                <td>
                    ${part.images.length ? part.images.map(image => `
                        <a href="${image.image_url}" target="_blank">
                            <img src="${image.image_url}" alt="${part.model}" class="img-thumbnail" style="max-width: 80px; max-height: 80px;">
                        </a>
                    `).join('') : 'Нет фото'}
                </td>
                <td>
                    <a href="/edit-part/${part.id}/" class="btn btn-warning btn-sm mb-1">✏️</a>
                    <a href="/delete-part/${part.id}/" class="btn btn-danger btn-sm">🗑️</a>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
});
