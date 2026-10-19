/**
 * Sales Data Analysis System - Main Frontend Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.app-sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });

        // Close sidebar on click outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            }
        });
    }

    // 2. Alert Dismiss Handlers
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alert = e.target.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // 3. Drag and Drop File Upload
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');

    if (dropzone && fileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileNameDisplay(files[0].name);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                updateFileNameDisplay(fileInput.files[0].name);
            }
        });
    }

    function updateFileNameDisplay(name) {
        const fileDisplay = document.getElementById('selectedFileName');
        if (fileDisplay) {
            fileDisplay.innerHTML = `<strong>Selected file:</strong> ${name}`;
            fileDisplay.style.display = 'block';
        }
    }

    // 4. Client-side Real-time Search Helper for Tables
    const tableSearchInput = document.getElementById('clientTableSearch');
    if (tableSearchInput) {
        tableSearchInput.addEventListener('keyup', (e) => {
            const query = e.target.value.toLowerCase();
            const targetTable = document.querySelector('.searchable-table tbody');
            if (!targetTable) return;

            const rows = targetTable.querySelectorAll('tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }
});
