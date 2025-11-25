// File: static/js/main.js

// Initialize tooltips, popovers, smooth scroll, flash message dismiss
document.addEventListener('DOMContentLoaded', function () {
  // Enable Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Enable Bootstrap popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });

  // Auto-dismiss flash messages
  const flashMessages = document.querySelectorAll('.alert');
  flashMessages.forEach(alert => {
    setTimeout(() => {
      const instance = bootstrap.Alert.getOrCreateInstance(alert);
      instance.close();
    }, 5000);
  });
});

// Handle image preview for file uploads
function previewImage(input, previewId) {
  const preview = document.getElementById(previewId);
  const file = input.files[0];
  const reader = new FileReader();

  reader.onload = function (e) {
    preview.src = e.target.result;
    preview.style.display = 'block';
  };

  if (file) {
    reader.readAsDataURL(file);
  }
}

// Form validation helper
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (form.checkValidity() === false) {
    event.preventDefault();
    event.stopPropagation();
  }
  form.classList.add('was-validated');
  return form.checkValidity();
}

// CSRF protection for AJAX
$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
      xhr.setRequestHeader("X-CSRFToken", $('meta[name="csrf-token"]').attr('content'));
    }
  }
});
