/* ========== Theme Toggle ========== */
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }
}

// Init theme
(function() {
    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
})();

/* ========== CSRF Token Helper ========== */
function getCSRF() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;
    const input = document.querySelector('input[name="csrf_token"]');
    return input ? input.value : '';
}

/* ========== Like / Bookmark / Follow ========== */
function toggleLike(articleId) {
    const form = new FormData();
    form.append('csrf_token', getCSRF());
    fetch(`/article/${articleId}/like`, { method: 'POST', body: form })
        .then(r => r.json())
        .then(data => {
            const btn = document.getElementById('like-btn');
            const count = document.getElementById('like-count');
            if (data.liked) {
                btn.className = 'btn btn-danger btn-action';
                btn.querySelector('i').className = 'bi bi-heart-fill';
            } else {
                btn.className = 'btn btn-outline-danger btn-action';
                btn.querySelector('i').className = 'bi bi-heart';
            }
            count.textContent = data.count;
        })
        .catch(() => showToast('操作失败', 'error'));
}

function toggleBookmark(articleId) {
    const form = new FormData();
    form.append('csrf_token', getCSRF());
    fetch(`/article/${articleId}/bookmark`, { method: 'POST', body: form })
        .then(r => r.json())
        .then(data => {
            const btn = document.getElementById('bookmark-btn');
            const count = document.getElementById('bookmark-count');
            if (data.bookmarked) {
                btn.className = 'btn btn-warning btn-action';
                btn.querySelector('i').className = 'bi bi-star-fill';
            } else {
                btn.className = 'btn btn-outline-warning btn-action';
                btn.querySelector('i').className = 'bi bi-star';
            }
            count.textContent = data.count;
        })
        .catch(() => showToast('操作失败', 'error'));
}

function toggleFollow(userId, btnEl) {
    const form = new FormData();
    form.append('csrf_token', getCSRF());
    fetch(`/user/${userId}/follow`, { method: 'POST', body: form })
        .then(r => r.json())
        .then(data => {
            const btn = btnEl || document.getElementById('follow-btn');
            if (data.following) {
                btn.className = btn.className.replace('btn-primary', 'btn-secondary').replace('btn-outline-primary', 'btn-secondary');
                btn.innerHTML = '<i class="bi bi-check-lg"></i> ' + (data.label || '已关注');
            } else {
                btn.className = btn.className.replace('btn-secondary', 'btn-primary');
                btn.innerHTML = '<i class="bi bi-plus-lg"></i> ' + (data.label || '关注');
            }
        })
        .catch(() => showToast('操作失败', 'error'));
}

/* ========== Comments ========== */
function submitComment(articleId, parentId, replyToUserId) {
    let content;
    if (parentId) {
        const input = document.getElementById(`reply-input-${parentId}`);
        content = input ? input.value.trim() : '';
    } else {
        content = document.getElementById('comment-input').value.trim();
    }
    if (!content) return false;

    const form = new FormData();
    form.append('csrf_token', getCSRF());
    form.append('content', content);
    if (parentId) form.append('parent_id', parentId);
    if (replyToUserId) form.append('reply_to_user_id', replyToUserId);

    fetch(`/article/${articleId}/comment`, { method: 'POST', body: form })
        .then(r => {
            if (r.ok) return r.json();
            return r.json().then(d => { throw new Error(d.error || '评论失败'); });
        })
        .then(() => location.reload())
        .catch(err => showToast(err.message || '评论失败', 'error'));
    return false;
}

function showReplyForm(commentId, userId) {
    const form = document.getElementById(`reply-form-${commentId}`);
    if (form) {
        form.classList.toggle('d-none');
        const input = document.getElementById(`reply-input-${commentId}`);
        if (input) input.focus();
    }
}

function deleteComment(commentId) {
    if (!confirm('确定删除此评论?')) return;
    const form = new FormData();
    form.append('csrf_token', getCSRF());
    fetch(`/comment/${commentId}/delete`, { method: 'POST', body: form })
        .then(r => r.json())
        .then(() => location.reload())
        .catch(() => showToast('删除失败', 'error'));
}

/* ========== Report ========== */
function submitReport(articleId) {
    const form = new FormData();
    form.append('csrf_token', getCSRF());
    form.append('article_id', articleId);
    form.append('reason', document.querySelector('#reportModal textarea[name="reason"]').value);
    fetch('/report', { method: 'POST', body: form })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast('举报已提交');
                const modal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
                if (modal) modal.hide();
            } else {
                showToast(data.error || '举报失败', 'error');
            }
        })
        .catch(() => showToast('举报失败', 'error'));
    return false;
}

/* ========== Delete Article ========== */
function deleteArticle(articleId) {
    if (!confirm('确定删除此文章?')) return;
    const form = new FormData();
    form.append('csrf_token', getCSRF());
    fetch(`/article/${articleId}/delete`, { method: 'POST', body: form })
        .then(() => { window.location.href = '/'; })
        .catch(() => showToast('删除失败', 'error'));
}

/* ========== Notifications ========== */
function updateNotifCount() {
    fetch('/notifications/count')
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('notif-count');
            if (badge) {
                if (data.count > 0) {
                    badge.style.display = '';
                    badge.textContent = data.count > 99 ? '99+' : data.count;
                } else {
                    badge.style.display = 'none';
                }
            }
        });
}

// Poll notifications every 30 seconds
if (document.querySelector('.notification-badge')) {
    updateNotifCount();
    setInterval(updateNotifCount, 30000);
}

/* ========== Toast ========== */
function showToast(message, type = 'success') {
    const container = document.querySelector('.toast-container') || (() => {
        const c = document.createElement('div');
        c.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        c.style.zIndex = '9999';
        document.body.appendChild(c);
        return c;
    })();
    const id = 'toast-' + Date.now();
    container.insertAdjacentHTML('beforeend', `
        <div id="${id}" class="toast align-items-center text-bg-${type === 'error' ? 'danger' : 'success'}" role="alert">
            <div class="d-flex"><div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>
        </div>
    `);
    new bootstrap.Toast(document.getElementById(id), { delay: 3000 }).show();
    setTimeout(() => document.getElementById(id)?.remove(), 4000);
}
