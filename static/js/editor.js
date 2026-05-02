/* ========== Editor Module ========== */
let currentEditor = 'markdown';
let quill = null;

// Initialize editors
document.addEventListener('DOMContentLoaded', function() {
    initMarkdownEditor();
    initRichTextEditor();
    initTagsInput();
});

function initMarkdownEditor() {
    const mdInput = document.getElementById('markdown-input');
    const mdPreview = document.getElementById('markdown-preview');
    if (!mdInput || !mdPreview) return;

    mdInput.addEventListener('input', function() {
        if (typeof marked !== 'undefined') {
            mdPreview.innerHTML = marked.parse(this.value);
        }
    });

    // Initial render
    if (mdInput.value && typeof marked !== 'undefined') {
        mdPreview.innerHTML = marked.parse(mdInput.value);
    }

    // Markdown image upload: paste or drag-and-drop
    mdInput.addEventListener('paste', function(e) {
        const items = e.clipboardData && e.clipboardData.items;
        if (!items) return;
        for (const item of items) {
            if (item.type.startsWith('image/')) {
                e.preventDefault();
                const file = item.getAsFile();
                uploadMarkdownImage(file, mdInput);
                break;
            }
        }
    });

    mdInput.addEventListener('drop', function(e) {
        const files = e.dataTransfer && e.dataTransfer.files;
        if (!files || !files.length) return;
        for (const file of files) {
            if (file.type.startsWith('image/')) {
                e.preventDefault();
                uploadMarkdownImage(file, mdInput);
                break;
            }
        }
    });
    mdInput.addEventListener('dragover', function(e) {
        e.preventDefault();
    });
}

function uploadMarkdownImage(file, mdInput) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('csrf_token', getCSRF());
    const placeholder = `![uploading...]\n`;
    const pos = mdInput.selectionStart;
    mdInput.value = mdInput.value.slice(0, pos) + placeholder + mdInput.value.slice(pos);
    fetch('/api/upload', { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            if (data.url) {
                mdInput.value = mdInput.value.replace(placeholder, `![](${data.url})\n`);
                mdInput.dispatchEvent(new Event('input'));
            }
        })
        .catch(() => {
            mdInput.value = mdInput.value.replace(placeholder, '');
            if (typeof showToast === 'function') showToast(I18N.uploadFailed, 'error');
        });
}

function initRichTextEditor() {
    const editorEl = document.getElementById('rich-editor');
    if (!editorEl || typeof Quill === 'undefined') return;

    quill = new Quill(editorEl, {
        theme: 'snow',
        placeholder: window.I18N ? I18N.editorPlaceholder : 'Start writing...',
        modules: {
            toolbar: {
                container: [
                    [{ 'header': [1, 2, 3, 4, 5, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'color': [] }, { 'background': [] }],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    ['blockquote', 'code-block'],
                    ['link', 'image'],
                    [{ 'align': [] }],
                    ['clean']
                ],
                handlers: {
                    image: function() {
                        const input = document.createElement('input');
                        input.setAttribute('type', 'file');
                        input.setAttribute('accept', 'image/*');
                        input.click();
                        input.onchange = () => {
                            const file = input.files[0];
                            if (!file) return;
                            const formData = new FormData();
                            formData.append('file', file);
                            formData.append('csrf_token', getCSRF());
                            fetch('/api/upload', { method: 'POST', body: formData })
                                .then(r => r.json())
                                .then(data => {
                                    if (data.url) {
                                        const range = quill.getSelection();
                                        quill.insertEmbed(range.index, 'image', data.url);
                                    }
                                })
                                .catch(() => showToast(I18N.uploadFailed, 'error'));
                        };
                    }
                }
            }
        }
    });
}

function switchEditor(type) {
    currentEditor = type;
    document.getElementById('editor-type-hidden').value = type;
}

function initTagsInput() {
    const input = document.getElementById('tags-input');
    const container = document.getElementById('tags-container');
    if (!input || !container) return;

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const name = this.value.trim();
            if (!name) return;

            // Check duplicates
            const existing = container.querySelectorAll('input[name="tags"]');
            for (const inp of existing) {
                if (inp.value === name) {
                    this.value = '';
                    return;
                }
            }

            const span = document.createElement('span');
            span.className = 'badge bg-primary d-flex align-items-center';
            const textNode = document.createTextNode(name);
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'tags';
            hiddenInput.value = name;
            const closeBtn = document.createElement('button');
            closeBtn.type = 'button';
            closeBtn.className = 'btn-close btn-close-white ms-1';
            closeBtn.style.fontSize = '0.6em';
            closeBtn.onclick = function() { this.parentElement.remove(); };
            span.appendChild(textNode);
            span.appendChild(hiddenInput);
            span.appendChild(closeBtn);
            container.appendChild(span);
            this.value = '';
        }
    });
}

function saveArticle(status) {
    document.getElementById('status-hidden').value = status;

    // Get content based on editor type
    if (currentEditor === 'markdown') {
        const mdInput = document.getElementById('markdown-input');
        document.getElementById('content-hidden').value = mdInput ? mdInput.value : '';
    } else if (quill) {
        document.getElementById('content-hidden').value = quill.root.innerHTML;
    }

    document.getElementById('editor-form').submit();
}

function loadVersion(versionId) {
    const articleId = document.querySelector('[name="article_id"]')?.value ||
                      window.location.pathname.split('/').pop();
    fetch(`/article/${articleId}/version/${versionId}`)
        .then(r => r.json())
        .then(data => {
            if (currentEditor === 'markdown') {
                document.getElementById('markdown-input').value = data.content;
                document.getElementById('markdown-input').dispatchEvent(new Event('input'));
            } else if (quill) {
                quill.root.innerHTML = data.content_html || data.content;
            }
            document.querySelector('[name="title"]').value = data.title;
            showToast(I18N.versionLoaded + data.version_number);
        });
}
