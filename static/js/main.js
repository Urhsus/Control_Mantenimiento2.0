// Función para inicializar los elementos dinámicos
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Manejo de formularios
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Formatear campos de moneda
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function(e) {
            const value = parseFloat(this.value.replace(/[^\d.-]/g, ''));
            if (!isNaN(value)) {
                this.value = value.toLocaleString('es-AR', {
                    style: 'currency',
                    currency: 'ARS'
                });
            }
        });
    });

    // Inicializar datepickers
    const datepickers = document.querySelectorAll('.datepicker');
    datepickers.forEach(input => {
        input.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            if (selectedDate > new Date()) {
                this.value = '';
                alert('La fecha no puede ser futura');
            }
        });
    });
});
