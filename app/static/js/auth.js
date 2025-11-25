// File: static/js/auth.js

// Registration form validation
document.addEventListener('DOMContentLoaded', function () {
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function (event) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');

            if (password.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity("Passwords don't match");
                event.preventDefault();
                event.stopPropagation();
            } else {
                confirmPassword.setCustomValidity('');
            }

            this.classList.add('was-validated');
        });

        // Show role-specific fields
        const roleSelect = document.getElementById('role');
        if (roleSelect) {
            roleSelect.addEventListener('change', function () {
                document.querySelectorAll('.role-fields').forEach(field => {
                    field.style.display = 'none';
                });

                const selectedFields = document.getElementById(this.value + 'Fields');
                if (selectedFields) {
                    selectedFields.style.display = 'block';
                }
            });
        }
    }

    // Password strength indicator
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            const strengthIndicator = document.getElementById('password-strength');
            if (strengthIndicator) {
                const strength = checkPasswordStrength(this.value);
                strengthIndicator.textContent = strength.text;
                strengthIndicator.className = 'password-strength ' + strength.class;
            }
        });
    }
});

function checkPasswordStrength(password) {
    if (password.length === 0) return { text: '', class: '' };
    if (password.length < 6) return { text: 'Weak', class: 'weak' };
    if (password.length < 10) return { text: 'Medium', class: 'medium' };
    return { text: 'Strong', class: 'strong' };
}
