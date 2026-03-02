// Smart Waste Monitoring System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Dashboard specific functions
    if (window.location.pathname === '/dashboard') {
        initDashboard();
    }

    // Home page animations
    if (window.location.pathname === '/') {
        initHomeAnimations();
    }
});

// Dashboard initialization
function initDashboard() {
    // Update timestamp
    updateTimestamp();
    
    // Auto-refresh detection data every 30 seconds
    setInterval(refreshDetectionData, 30000);
    
    // Initialize file upload preview
    initFileUploadPreview();
}

// Update timestamp display
function updateTimestamp() {
    const timestampElement = document.getElementById('lastUpdate');
    if (timestampElement) {
        timestampElement.textContent = new Date().toLocaleTimeString();
    }
}

// Refresh detection data via AJAX
async function refreshDetectionData() {
    try {
        const response = await fetch('/api/detections');
        if (response.ok) {
            const detections = await response.json();
            updateDetectionStats(detections);
            updateTimestamp();
        }
    } catch (error) {
        console.error('Error refreshing detection data:', error);
    }
}

// Update detection statistics
function updateDetectionStats(detections) {
    const totalElement = document.getElementById('totalDetections');
    const alertsElement = document.getElementById('wasteAlerts');
    
    if (totalElement) {
        totalElement.textContent = detections.length;
    }
    
    if (alertsElement) {
        const wasteCount = detections.filter(d => d.status === 'WASTE DETECTED').length;
        alertsElement.textContent = wasteCount;
    }
}

// File upload preview
function initFileUploadPreview() {
    const fileInput = document.getElementById('imageFile');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

// Show image preview
function showImagePreview(imageSrc) {
    const resultDiv = document.getElementById('uploadResult');
    if (resultDiv) {
        resultDiv.innerHTML = `
            <div class="mt-3">
                <h6>Preview:</h6>
                <img src="${imageSrc}" class="img-thumbnail" style="max-height: 200px;" alt="Preview">
            </div>
        `;
    }
}

// Home page animations
function initHomeAnimations() {
    // Animate feature cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card, .feature-card, .team-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Counter animation for statistics
    animateCounters();
}

// Animate number counters
function animateCounters() {
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-count'));
        const duration = 2000; // 2 seconds
        const step = target / (duration / 16); // 60fps
        let current = 0;

        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.floor(current);
        }, 16);
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Download detection data as CSV
function downloadDetectionData() {
    fetch('/api/detections')
        .then(response => response.json())
        .then(data => {
            const csv = convertToCSV(data);
            downloadCSV(csv, 'waste_detections.csv');
        })
        .catch(error => {
            console.error('Error downloading data:', error);
            showNotification('Failed to download data', 'error');
        });
}

// Convert JSON to CSV
function convertToCSV(data) {
    if (!data.length) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => {
            const value = row[header];
            return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        }).join(','))
    ].join('\n');
    
    return csvContent;
}

// Download CSV file
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Image analysis helper
async function analyzeImageFile(file) {
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error analyzing image:', error);
        throw error;
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+R or F5 - Refresh dashboard data
    if ((e.ctrlKey && e.key === 'r') || e.key === 'F5') {
        if (window.location.pathname === '/dashboard') {
            e.preventDefault();
            refreshDetectionData();
            showNotification('Dashboard refreshed!', 'info');
        }
    }
    
    // Escape - Close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});

// Service Worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// Export functions for global use
window.SmartWaste = {
    showNotification,
    formatTimestamp,
    copyToClipboard,
    downloadDetectionData,
    analyzeImageFile,
    refreshDetectionData
};