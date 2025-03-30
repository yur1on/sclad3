document.addEventListener('DOMContentLoaded', function() {
    const isMobile = window.innerWidth <= 768;
    if (!isMobile) return;

    const cardsContainer = document.getElementById('parts-cards-container');
    if (!cardsContainer) {
        console.error('Cards container not found');
        return;
    }

    const deviceButtons = document.getElementById('device-buttons');
    const brandButtons = document.getElementById('brand-buttons');
    const modelButtons = document.getElementById('model-buttons');
    const partTypeButtons = document.getElementById('part-type-buttons');

    const brandButtonsContainer = document.getElementById('brand-buttons-container');
    const modelButtonsContainer = document.getElementById('model-buttons-container');
    const partTypeButtonsContainer = document.getElementById('part-type-buttons-container');

    let selectedDevice = '';
    let selectedBrand = '';
    let selectedModel = '';
    let selectedPartType = '';

    function removeParenthesesText(text) {
        return text.replace(/\s*\(.*?\)\s*/g, '');
    }

    fetch('/get-devices/')
        .then(response => response.json())
        .then(data => {
            mobilePopulateButtons(deviceButtons, data.devices, mobileHandleDeviceClick);
            mobileUpdateDisplay();
        })
        .catch(error => console.error('Error loading devices:', error));

    function mobileHandleDeviceClick(device) {
        mobileSetActiveButton(deviceButtons, device);
        selectedDevice = device;
        mobileResetFilters('brand');
        fetch(`/get-brands/?device=${device}`)
            .then(response => response.json())
            .then(data => {
                brandButtonsContainer.style.display = 'block';
                mobilePopulateButtons(brandButtons, data.brands, mobileHandleBrandClick);
                mobileUpdateDisplay();
            })
            .catch(error => console.error('Error loading brands:', error));
    }

    function mobileHandleBrandClick(brand) {
        mobileSetActiveButton(brandButtons, brand);
        selectedBrand = brand;
        mobileResetFilters('model');
        fetch(`/get-models/?device=${selectedDevice}&brand=${brand}`)
            .then(response => response.json())
            .then(data => {
                modelButtonsContainer.style.display = 'block';
                mobilePopulateButtons(modelButtons, data.models, mobileHandleModelClick, true);
                mobileUpdateDisplay();
            })
            .catch(error => console.error('Error loading models:', error));
    }

    function mobileHandleModelClick(model) {
        mobileSetActiveButton(modelButtons, model);
        selectedModel = model;
        mobileResetFilters('partType');
        fetch(`/get-part-types/?device=${selectedDevice}&brand=${selectedBrand}&model=${model}`)
            .then(response => response.json())
            .then(data => {
                partTypeButtonsContainer.style.display = 'block';
                mobilePopulateButtons(partTypeButtons, data.part_types, mobileHandlePartTypeClick, true);
                mobileUpdateDisplay();
            })
            .catch(error => console.error('Error loading part types:', error));
    }

    function mobileHandlePartTypeClick(partType) {
        mobileSetActiveButton(partTypeButtons, partType);
        selectedPartType = partType;
        mobileUpdateDisplay();
    }

    function mobileResetFilters(level) {
        if (level === 'brand') {
            selectedBrand = '';
            selectedModel = '';
            selectedPartType = '';
            brandButtons.innerHTML = '';
            modelButtons.innerHTML = '';
            partTypeButtons.innerHTML = '';
            modelButtonsContainer.style.display = 'none';
            partTypeButtonsContainer.style.display = 'none';
        } else if (level === 'model') {
            selectedModel = '';
            selectedPartType = '';
            modelButtons.innerHTML = '';
            partTypeButtons.innerHTML = '';
            partTypeButtonsContainer.style.display = 'none';
        } else if (level === 'partType') {
            selectedPartType = '';
            partTypeButtons.innerHTML = '';
        }
    }

    function mobilePopulateButtons(container, items, clickHandler, isCompact = false) {
        container.innerHTML = '';
        items.sort((a, b) => a.localeCompare(b));
        items.forEach(item => {
            const button = document.createElement('button');
            button.classList.add('mobile-filter-btn');
            if (isCompact) button.style.fontSize = '0.8rem';
            button.textContent = removeParenthesesText(item);
            button.addEventListener('click', () => clickHandler(item));
            container.appendChild(button);
        });
    }

    function mobileSetActiveButton(container, selectedItem) {
        Array.from(container.children).forEach(button => {
            button.classList.remove('mobile-btn-active');
        });
        const selectedButton = Array.from(container.children).find(button =>
            removeParenthesesText(button.textContent) === removeParenthesesText(selectedItem)
        );
        if (selectedButton) {
            selectedButton.classList.add('mobile-btn-active');
        }
    }

    function mobileUpdateDisplay() {
        fetch(`/get-parts/?device=${selectedDevice}&brand=${selectedBrand}&model=${selectedModel}&part_type=${selectedPartType}`)
            .then(response => response.json())
            .then(data => {
                data.parts.sort((a, b) => b.id - a.id);
                mobileDisplayCards(data.parts);
            })
            .catch(error => console.error('Error fetching parts:', error));
    }

    function mobileDisplayCards(parts) {
        const allCards = document.querySelectorAll('.part-card');
        allCards.forEach(card => card.style.display = 'none');

        if (!parts || parts.length === 0) {
            cardsContainer.innerHTML = '<p class="text-center">Запчасти не найдены</p>';
            return;
        }

        parts.forEach(part => {
            const card = document.querySelector(`.part-card[data-part-id="${part.id}"]`);
            if (card) {
                card.style.display = 'flex';
            }
        });
    }

    // Экспортируем функции для вызова из HTML
    window.mobileFilterByDevice = mobileHandleDeviceClick;
    window.mobileFilterByBrand = mobileHandleBrandClick;
    window.mobileFilterByModel = mobileHandleModelClick;
    window.mobileFilterByPartType = mobileHandlePartTypeClick;
});