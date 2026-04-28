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
}

function initRichTextEditor() {
    const editorEl = document.getElementById('rich-editor');
    if (!editorEl || typeof Quill === 'undefined') return;

    quill = new Quill(editorEl, {
        theme: 'snow',
        placeholder: '开始写作...',
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
                                .catch(() => showToast('图片上传失败', 'error'));
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
            span.innerHTML = `${name}<input type="hidden" name="tags" value="${name}"><button type="button" class="btn-close btn-close-white ms-1" style="font-size:0.6em" onclick="this.parentElement.remove()"></button>`;
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
            showToast('已加载版本 v' + data.version_number);
        });
}
