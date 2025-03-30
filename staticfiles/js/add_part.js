document.addEventListener("DOMContentLoaded", function () {
    const deviceInput = document.getElementById("id_device");
    const brandInput = document.getElementById("id_brand");
    const modelInput = document.getElementById("id_model");
    const partTypeInput = document.getElementById("id_part_type");
    const colorInputContainer = document.getElementById("color_input_container");
    const colorInput = document.getElementById("id_color");
    const chipMarkingContainer = document.getElementById("chip_marking_container");
    const chipMarkingInput = document.getElementById("id_chip_marking");
    const form = document.querySelector("form");

    // Обработчик для изменения устройства
    deviceInput.addEventListener("change", () => {
        clearFormFields();
        updateDynamicFields({ device: deviceInput.value });
    });

    // Обработчик для изменения бренда
    brandInput.addEventListener("change", () => {
        clearModelAndPartType();
        updateDynamicFields({ device: deviceInput.value, brand: brandInput.value });
    });

    // Обработчик для изменения типа запчасти
    partTypeInput.addEventListener("change", () => {
        updateDynamicFields({ device: deviceInput.value, part_type: partTypeInput.value });
        toggleColorInput(partTypeInput.value);
        toggleChipMarking(partTypeInput.value);
    });

    // Обработчик для отправки формы
    form.addEventListener("submit", function () {
        if (partTypeInput.value === "Микросхема" && chipMarkingInput.value.trim() !== "") {
            partTypeInput.value += ` ${chipMarkingInput.value.trim()}`;
        }
    });

    // Функция для очистки всех связанных полей
    function clearFormFields() {
        brandInput.value = '';
        modelInput.value = '';
        partTypeInput.value = '';
        colorInputContainer.style.display = "none";
        chipMarkingContainer.style.display = "none";
        colorInput.value = '';
        clearDatalists(["brands", "models", "part_types", "colors"]);
    }

    // Функция для очистки только модели и типа запчасти
    function clearModelAndPartType() {
        modelInput.value = '';
        partTypeInput.value = '';
        colorInputContainer.style.display = "none";
        chipMarkingContainer.style.display = "none";
        colorInput.value = '';
        clearDatalists(["models", "part_types", "colors"]);
    }

    // Функция для обновления динамических данных с сервера
    function updateDynamicFields(params) {
        fetch(`/get_dynamic_data/?${new URLSearchParams(params)}`)
            .then((response) => response.json())
            .then((data) => {
                if (data.brands) updateDatalist("brands", data.brands);
                if (data.models) updateDatalist("models", data.models);
                if (data.part_types) updateDatalist("part_types", data.part_types);
                if (data.colors) updateDatalist("colors", data.colors);
                if (data.conditions) updateDatalist("conditions", data.conditions);
            })
            .catch((error) => console.error("Ошибка загрузки данных:", error));
    }

    // Функция для обновления содержимого datalist
    function updateDatalist(datalistId, items) {
        const datalist = document.getElementById(datalistId);
        datalist.innerHTML = "";
        items.forEach((item) => {
            const option = document.createElement("option");
            option.value = item;
            datalist.appendChild(option);
        });
    }

    // Функция для очистки datalist
    function clearDatalists(datalistIds) {
        datalistIds.forEach((id) => {
            const datalist = document.getElementById(id);
            datalist.innerHTML = "";
        });
    }

    // Функция для отображения или скрытия поля цвета в зависимости от типа запчасти
    function toggleColorInput(partType) {
        if (partType) {
            fetch(`/get_dynamic_data/?device=${deviceInput.value}&part_type=${partType}`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.colors && data.colors.length > 0) {
                        updateDatalist("colors", data.colors);
                        colorInputContainer.style.display = "block";
                    } else {
                        colorInputContainer.style.display = "none";
                        colorInput.value = '';
                    }
                })
                .catch((error) => console.error("Ошибка загрузки цветов:", error));
        } else {
            colorInputContainer.style.display = "none";
            colorInput.value = '';
        }
    }

    // Функция для отображения или скрытия контейнера маркировки чипа
    function toggleChipMarking(partType) {
        if (partType === "Микросхема") {
            chipMarkingContainer.style.display = "block";
        } else {
            chipMarkingContainer.style.display = "none";
        }
    }
});
