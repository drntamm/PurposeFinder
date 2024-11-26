// Ikigai Purpose Finder - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Ikigai Purpose Finder JavaScript loaded');

    // Form validation and interactivity
    const assessmentForm = document.querySelector('form');
    if (assessmentForm) {
        assessmentForm.addEventListener('submit', function(event) {
            const checkboxes = assessmentForm.querySelectorAll('input[type="checkbox"]');
            let atLeastOneChecked = false;

            checkboxes.forEach(function(checkbox) {
                const sectionCheckboxes = assessmentForm.querySelectorAll(`input[name="${checkbox.name}"]:checked`);
                if (sectionCheckboxes.length > 0) {
                    atLeastOneChecked = true;
                }
            });

            if (!atLeastOneChecked) {
                event.preventDefault();
                alert('Please select at least one option in each section.');
            }
        });
    }

    // Venn diagram interactivity
    const vennCircles = document.querySelectorAll('.venn-circle');
    vennCircles.forEach(function(circle) {
        circle.addEventListener('mouseover', function() {
            this.style.opacity = '0.8';
        });

        circle.addEventListener('mouseout', function() {
            this.style.opacity = '0.6';
        });
    });
});
