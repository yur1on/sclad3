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




document.addEventListener('DOMContentLoaded', function() {
    const regionSelect = document.getElementById('id_region');
    const citySelect = document.getElementById('id_city');

    const regionAdvSelect = document.getElementById('id_region_adv');
    const cityAdvSelect = document.getElementById('id_city_adv');

    // Функция для обновления списка городов
    function updateCitySelect(regionSelect, citySelect, data) {
        const selectedRegion = regionSelect.value;
        citySelect.innerHTML = '';

        if (data[selectedRegion]) {
            data[selectedRegion].forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                citySelect.appendChild(option);
            });
        } else {
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Выберите город';
            citySelect.appendChild(defaultOption);
        }
    }

    // Загрузка данных о регионах и городах с сервера
    fetch('/get_regions_and_cities/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка загрузки данных');
            }
            return response.json();
        })
        .then(data => {
            // Обработчик для основного поиска
            if (regionSelect && citySelect) {
                regionSelect.addEventListener('change', function() {
                    updateCitySelect(regionSelect, citySelect, data);
                });

                // Если регион уже выбран, обновить города
                if (regionSelect.value) {
                    updateCitySelect(regionSelect, citySelect, data);
                }
            }

            // Обработчик для расширенного поиска
            if (regionAdvSelect && cityAdvSelect) {
                regionAdvSelect.addEventListener('change', function() {
                    updateCitySelect(regionAdvSelect, cityAdvSelect, data);
                });

                // Если регион уже выбран в расширенном поиске, обновить города
                if (regionAdvSelect.value) {
                    updateCitySelect(regionAdvSelect, cityAdvSelect, data);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Ошибка загрузки данных';
            if (citySelect) citySelect.appendChild(defaultOption);
            if (cityAdvSelect) cityAdvSelect.appendChild(defaultOption);
        });

    // Логика переключения между обычным и расширенным поиском
    const toggleButton = document.getElementById('toggle-advanced-search');
    const basicSearch = document.getElementById('basic-search');
    const advancedSearch = document.getElementById('advanced-search');

    if (toggleButton && basicSearch && advancedSearch) {
        toggleButton.addEventListener('click', function() {
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
    }
});
