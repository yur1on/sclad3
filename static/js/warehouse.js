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
