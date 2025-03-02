function toggleDropdown(id) {
    var dropdown = document.getElementById(id);
    dropdown.classList.toggle('show');
}

function toggleSidebar() {
    var sidebar = document.getElementById('dashboard-sidebar');
    var content = document.getElementById('dashboard-content');
    var content = document.querySelector('.contenedor-principal');
    sidebar.classList.toggle('sidebar-reduced');
    sidebar.classList.toggle('collapsed');
    content.classList.toggle('expanded');
}

// Manejar clics en los enlaces del sidebar
document.addEventListener('DOMContentLoaded', function () {
    // Ocultar todas las secciones de contenido al cargar la página
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    // Mostrar la primera sección por defecto
    document.querySelector('.content-section').style.display = 'block';

    // Manejar clics en los enlaces del sidebar
    document.querySelectorAll('.contenedor-menu a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault(); // Prevenir el comportamiento predeterminado del enlace

            const targetId = this.getAttribute('href').substring(1);
            document.querySelectorAll('.content-section').forEach(section => {
                section.style.display = 'none';
            });
            document.getElementById(targetId).style.display = 'block';
        });
    });

    // Evitar que los clics dentro del menú desplegable cierren el menú
    document.querySelectorAll('.dropdown-content a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.stopPropagation(); // Evitar que el evento se propague al contenedor principal
        });
    });
});

// Añadir clase condicional al footer cuando el sidebar esté presente
document.addEventListener('DOMContentLoaded', function () {
    var footer = document.querySelector('.footer');
    if (footer) {
        footer.classList.add('with-sidebar');
    }
});