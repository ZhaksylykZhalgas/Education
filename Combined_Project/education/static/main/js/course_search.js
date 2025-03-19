document.addEventListener('DOMContentLoaded', () => {
    const searchIcon = document.querySelector('.search-icon');
    const searchForm = document.querySelector('.search-container form');
    const searchInput = document.querySelector('.search-bar');

    if (searchIcon && searchForm && searchInput) {
        searchIcon.addEventListener('click', (event) => {
            if (!searchInput.value.trim()) { // Проверяем, что поле не пустое
                alert('Пожалуйста, введите текст для поиска!'); // Сообщение пользователю
                event.preventDefault(); // Отменяем отправку формы
            } else {
                searchForm.submit(); // Отправляем форму
            }
        });
    }
});
