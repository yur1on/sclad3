<script>
    document.addEventListener("DOMContentLoaded", function () {
        var deviceButtons = document.getElementById("device-buttons");
        var brandButtonsContainer = document.getElementById("brand-buttons");
        var partsTable = document.getElementById("parts-table-container");
        var showDevicesButton = document.getElementById("show-devices-btn");

        // Изначально скрываем кнопки устройств и брендов
        deviceButtons.style.display = "none";
        brandButtonsContainer.style.display = "none";

        // Показать кнопки устройств и скрыть таблицу
        showDevicesButton.addEventListener("click", function () {
            partsTable.style.display = "none";
            deviceButtons.style.display = "block";
            brandButtonsContainer.style.display = "none";
        });

        // Отображение брендов по выбранному устройству
        function showBrands(device) {
            // Скрываем кнопки устройств, показываем кнопки брендов
            deviceButtons.style.display = "none";
            brandButtonsContainer.style.display = "block";

            // Получаем кнопки брендов, относящихся к выбранному устройству
            const brandButtons = document.getElementsByClassName('brand-btn');
            for (let btn of brandButtons) {
                if (btn.dataset.device === device) {
                    btn.style.display = "inline-block";
                } else {
                    btn.style.display = "none";
                }
            }
        }

        // Добавляем обработчики событий на кнопки устройств
        const deviceButtonsList = document.getElementsByClassName('device-btn');
        for (let btn of deviceButtonsList) {
            btn.addEventListener("click", function () {
                showBrands(btn.dataset.device);
            });
        }
    });
</script>
