document.addEventListener('DOMContentLoaded', function() {
    const deviceButtonsContainer = document.getElementById('device-buttons-container');
    const brandButtonsContainer = document.getElementById('brand-buttons-container');
    const modelButtonsContainer = document.getElementById('model-buttons-container');
    const partTypeButtonsContainer = document.getElementById('part-type-buttons-container');

    const deviceButtons = document.getElementById('device-buttons');
    const brandButtons = document.getElementById('brand-buttons');
    const modelButtons = document.getElementById('model-buttons');
    const partTypeButtons = document.getElementById('part-type-buttons');

    let selectedDevice = '';
    let selectedBrand = '';
    let selectedModel = '';
    let selectedPartType = '';

    function removeParenthesesText(text) {
    return text.replace(/\s*\(.*?\)\s*/g, ''); // Удаляем текст в скобках
}


    // Загрузка кнопок для устройств при загрузке страницы
    fetch('/get-devices/')
        .then(response => response.json())
        .then(data => {
            populateButtons(deviceButtons, data.devices, handleDeviceClick);
        });

    // Обработка нажатия на устройство
    function handleDeviceClick(device) {
        selectedDevice = device;

        // Сброс брендов, моделей и типов запчастей при изменении устройства
        selectedBrand = '';
        selectedModel = '';
        selectedPartType = '';

        brandButtons.innerHTML = '';  // Очищаем старые кнопки брендов
        modelButtons.innerHTML = '';  // Очищаем старые кнопки моделей
        partTypeButtons.innerHTML = '';  // Очищаем старые кнопки типов запчастей
        modelButtonsContainer.style.display = 'none';
        partTypeButtonsContainer.style.display = 'none';

        // Запрашиваем бренды для выбранного устройства
        fetch(`/get-brands/?device=${device}`)
            .then(response => response.json())
            .then(data => {
                brandButtonsContainer.style.display = 'block';
                populateButtons(brandButtons, data.brands, handleBrandClick);
            });

        setActiveButton(deviceButtons, device);
        updateTable();
    }

    // Обработка нажатия на бренд
    function handleBrandClick(brand) {
        selectedBrand = brand;

        // Сброс моделей и типов запчастей при изменении бренда
        selectedModel = '';
        selectedPartType = '';

        modelButtons.innerHTML = '';  // Очищаем старые кнопки моделей
        partTypeButtons.innerHTML = '';  // Очищаем старые кнопки типов запчастей
        partTypeButtonsContainer.style.display = 'none';

        // Запрашиваем модели для выбранного устройства и бренда
        fetch(`/get-models/?device=${selectedDevice}&brand=${brand}`)
            .then(response => response.json())
            .then(data => {
                modelButtonsContainer.style.display = 'block';
                populateButtons(modelButtons, data.models, handleModelClick, true);
            });

        setActiveButton(brandButtons, brand);
        updateTable();
    }

    // Обработка нажатия на модель
    function handleModelClick(model) {
        selectedModel = model;

        // Сброс типов запчастей при изменении модели
        selectedPartType = '';

        partTypeButtons.innerHTML = '';  // Очищаем старые кнопки типов запчастей

        // Запрашиваем типы запчастей для выбранных устройства, бренда и модели
        fetch(`/get-part-types/?device=${selectedDevice}&brand=${selectedBrand}&model=${model}`)
            .then(response => response.json())
            .then(data => {
                partTypeButtonsContainer.style.display = 'block';
                populateButtons(partTypeButtons, data.part_types, handlePartTypeClick, true);
            });

        setActiveButton(modelButtons, model);
        updateTable();
    }

    // Обработка нажатия на тип запчасти
    function handlePartTypeClick(partType) {
        selectedPartType = partType;

        // Запрашиваем запчасти для выбранных устройства, бренда, модели и типа запчасти
        fetch(`/get-parts/?device=${selectedDevice}&brand=${selectedBrand}&model=${selectedModel}&part_type=${partType}`)
            .then(response => response.json())
            .then(data => {
                displayParts(data.parts);  // Обновляем таблицу запчастей
            });

        setActiveButton(partTypeButtons, partType);
    }

    function populateButtons(container, items, clickHandler, isCompact = false) {
        container.innerHTML = '';  // Очищаем контейнер от старых кнопок

        // Сортируем элементы по алфавиту
        items.sort((a, b) => a.localeCompare(b));

        items.forEach(item => {
            const button = document.createElement('button');
            button.classList.add('btn', 'btn-primary', 'me-2', 'mb-2');  // Стандартные классы для всех кнопок

            if (isCompact) {
                button.classList.add('btn-compact');  // Добавляем 'btn-compact' для кнопок моделей и типов запчастей
            }

            button.textContent = removeParenthesesText(item); // Убираем текст в скобках
            button.addEventListener('click', () => clickHandler(item));
            container.appendChild(button);
        });
    }


    // Функция для изменения активной кнопки (подсвечивание)
    function setActiveButton(container, selectedItem) {
        Array.from(container.children).forEach(button => {
            button.classList.remove('btn-active');
            button.classList.add('btn-primary');
        });

        const selectedButton = Array.from(container.children).find(button => button.textContent === selectedItem);
        if (selectedButton) {
            selectedButton.classList.remove('btn-primary');
            selectedButton.classList.add('btn-active');
        }
    }

    // Функция для обновления таблицы с запчастями
    function updateTable() {
        fetch(`/get-parts/?device=${selectedDevice}&brand=${selectedBrand}&model=${selectedModel}&part_type=${selectedPartType}`)
            .then(response => response.json())
            .then(data => {
                displayParts(data.parts);
            });
    }


// Функция для отображения запчастей в таблице
function displayParts(parts) {
    const tbody = document.querySelector('#parts-table-body');
    tbody.innerHTML = ''; // Очищаем старые данные таблицы

    parts.forEach(part => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${removeParenthesesText(part.device)}</td>
            <td>${removeParenthesesText(part.brand)}</td>
            <td>${removeParenthesesText(part.model)}</td>
            <td>${removeParenthesesText(part.part_type)}</td>
            <td>
                <div>
                    <strong>Цвет:</strong> ${part.color || 'Не указан'} |
                    <strong>Цена:</strong> ${part.price} |
                    <strong>Количество:</strong> ${part.quantity}
                </div>
                <div>
                    ${part.condition ? `<strong>Состояние:</strong> ${part.condition}` : ''}
                    ${part.note ? `<strong>, Примечание:</strong> ${part.note}</span>` : '<strong>, Примечание:</strong><span> Нет примечаний</span>'}
                </div>
            </td>
            <td>
                ${part.images.length ? `
                    <a href="#" data-bs-toggle="modal" data-bs-target="#imageModal-${part.id}">
                        <img src="${part.images[0].image_url}" alt="${part.model}" class="img-thumbnail" style="max-width: 80px; max-height: 80px;">
                    </a>
                ` : 'Нет фото'}
            </td>
            <td>
                <a href="/edit-part/${part.id}/" class="btn btn-warning btn-sm mb-1">✏️</a>
                <a href="/delete-part/${part.id}/" class="btn btn-danger btn-sm">🗑️</a>
            </td>
        `;

        tbody.appendChild(row);

        // Если у запчасти есть изображения, создаем модальное окно для их отображения
        if (part.images.length) {
            const modalHtml = `
                <div class="modal fade" id="imageModal-${part.id}" tabindex="-1" aria-labelledby="imageModalLabel-${part.id}" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-body">
                                <!-- Карусель -->
                                <div id="carouselPartImages-${part.id}" class="carousel slide" data-bs-ride="carousel">
                                    <div class="carousel-inner">
                                        ${part.images.map((image, index) => `
                                            <div class="carousel-item ${index === 0 ? 'active' : ''}">
                                                <img src="${image.image_url}" class="d-block w-100" alt="${part.model}" style="max-height: 500px; object-fit: contain;">
                                            </div>
                                        `).join('')}
                                    </div>
                                    <!-- Навигация влево/вправо -->
                                    <button class="carousel-control-prev" type="button" data-bs-target="#carouselPartImages-${part.id}" data-bs-slide="prev">
                                        <span class="carousel-control-prev-icon" aria-hidden="true" style="background-color: black; padding: 10px;"></span>
                                        <span class="visually-hidden">Предыдущий</span>
                                    </button>
                                    <button class="carousel-control-next" type="button" data-bs-target="#carouselPartImages-${part.id}" data-bs-slide="next">
                                        <span class="carousel-control-next-icon" aria-hidden="true" style="background-color: black; padding: 10px;"></span>
                                        <span class="visually-hidden">Следующий</span>
                                    </button>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Добавляем модальное окно в конец тела документа
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
    });
}



});
