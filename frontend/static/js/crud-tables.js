/**
 * Open a modal by ID
 */
function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

/**
 * Close a modal by ID
 */
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

/**
 * Populate form fields from data object
 */
function populateForm(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;
    Object.keys(data).forEach(key => {
        const field = form.querySelector(`[name="${key}"]`);
        if (field) field.value = data[key] || '';
    });
}

/**
 * Collect form data as object
 */
function collectFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return {};
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    return data;
}

/**
 * Handle create/update form submission
 */
async function submitForm(apiUrl, method, formId, modalId) {
    const data = collectFormData(formId);
    try {
        const result = await apiFetch(apiUrl, {
            method: method,
            body: data,
        });
        if (result.success) {
            showToast(method === 'POST' ? 'נוצר בהצלחה' : 'עודכן בהצלחה', 'success');
            closeModal(modalId);
            setTimeout(() => window.location.reload(), 500);
        }
    } catch (e) {
        // Error already shown by apiFetch
    }
}

/**
 * Handle delete with confirmation
 */
async function deleteRecord(apiUrl, name) {
    if (!confirm(`האם אתה בטוח שברצונך למחוק את "${name}"?`)) return;
    try {
        const result = await apiFetch(apiUrl, { method: 'DELETE' });
        if (result.success) {
            showToast('נמחק בהצלחה', 'success');
            setTimeout(() => window.location.reload(), 500);
        }
    } catch (e) {
        // Error already shown by apiFetch
    }
}

/**
 * Initialize search with debounce
 */
function initSearch(inputId, paramName = 'search') {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener('input', debounce((e) => {
        const url = new URL(window.location);
        url.searchParams.set(paramName, e.target.value);
        url.searchParams.delete('page');
        window.location.href = url.toString();
    }, 500));
}

/**
 * Navigate to a page
 */
function goToPage(page) {
    const url = new URL(window.location);
    url.searchParams.set('page', page);
    window.location.href = url.toString();
}

/**
 * Filter by status
 */
function filterByStatus(status) {
    const url = new URL(window.location);
    if (status) {
        url.searchParams.set('status', status);
    } else {
        url.searchParams.delete('status');
    }
    url.searchParams.delete('page');
    window.location.href = url.toString();
}
