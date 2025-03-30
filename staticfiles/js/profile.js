document.addEventListener('DOMContentLoaded', function () {
    const regionSelect = document.getElementById('id_region');
    const citySelect = document.getElementById('id_city');

    // Функция для загрузки данных регионов и городов с сервера
    function loadRegionsAndCities() {
        fetch('/regions_and_cities/')  // Путь к вашему API для загрузки регионов и городов
            .then(response => response.json())
            .then(data => {
                // Заполняем селект с регионами
                Object.keys(data).forEach(function (region) {
                    const option = document.createElement('option');
                    option.value = region;
                    option.text = region;
                    regionSelect.appendChild(option);
                });

                // Если область уже выбрана, загружаем соответствующие города
                if (regionSelect.value) {
                    loadCities(regionSelect.value, data);
                }
            })
            .catch(error => {
                console.log('Error loading regions and cities:', error);
            });
    }

    // Функция для загрузки городов на основе выбранной области
    function loadCities(region, data) {
        citySelect.innerHTML = '';  // Очищаем предыдущие города
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.text = 'Выберите город';
        citySelect.appendChild(defaultOption); // Добавляем опцию по умолчанию

        if (data[region]) {
            data[region].forEach(function (city) {
                const option = document.createElement('option');
                option.value = city;
                option.text = city;
                citySelect.appendChild(option);
            });
        } else {
            console.log('No cities found for region:', region);
        }
    }

    // При изменении области загружаем города
    regionSelect.addEventListener('change', function () {
        fetch('/regions_and_cities/')  // Путь к вашему API для загрузки данных
            .then(response => response.json())
            .then(data => loadCities(regionSelect.value, data))
            .catch(error => {
                console.log('Error loading cities:', error);
            });
    });

    // Загружаем регионы и города при первой загрузке страницы
    loadRegionsAndCities();
});
