document.addEventListener('DOMContentLoaded', function () {
    const stars = document.querySelectorAll('.rating-star');
    const ratingInput = document.getElementById('rating-input');

    stars.forEach(star => {
        star.addEventListener('mouseover', function () {
            const value = this.getAttribute('data-value');
            highlightStars(value);
        });

        star.addEventListener('mouseout', function () {
            const currentValue = ratingInput.value;
            highlightStars(currentValue);
        });

        star.addEventListener('click', function () {
            const value = this.getAttribute('data-value');
            ratingInput.value = Math.min(value, 5); // Убедитесь, что оценка не больше 5
            setSelectedStars(ratingInput.value);
        });
    });

    function highlightStars(value) {
        stars.forEach(star => {
            if (star.getAttribute('data-value') <= value) {
                star.classList.add('selected');
            } else {
                star.classList.remove('selected');
            }
        });
    }

    function setSelectedStars(value) {
        stars.forEach(star => {
            if (star.getAttribute('data-value') <= value) {
                star.classList.add('selected');
            } else {
                star.classList.remove('selected');
            }
        });
    }

    // Устанавливаем начальное состояние звезд
    setSelectedStars(ratingInput.value);
});
