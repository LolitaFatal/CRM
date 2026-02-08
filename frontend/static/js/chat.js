async function sendChat(event) {
    if (event) event.preventDefault();

    const input = document.getElementById('chatInput');
    const container = document.getElementById('chatMessages');
    const question = input.value.trim();
    if (!question) return;

    // Add user message
    const userBubble = document.createElement('div');
    userBubble.className = 'flex flex-col items-end gap-1';
    userBubble.innerHTML = `
        <div class="bg-primary text-white p-3 rounded-2xl rounded-tl-none text-sm max-w-[80%]">
            ${escapeHtml(question)}
        </div>
        <span class="text-[10px] text-slate-400 ml-2">${new Date().toLocaleTimeString('he-IL', {hour: '2-digit', minute: '2-digit'})}</span>
    `;
    container.appendChild(userBubble);
    input.value = '';
    scrollToBottom();

    // Add typing indicator
    const typingEl = document.createElement('div');
    typingEl.id = 'typing-indicator';
    typingEl.className = 'flex flex-col items-start gap-1';
    typingEl.innerHTML = `
        <div class="bg-slate-100 p-3 rounded-2xl rounded-tr-none text-sm flex gap-1.5 items-center">
            <div class="size-2 bg-slate-400 rounded-full typing-dot"></div>
            <div class="size-2 bg-slate-400 rounded-full typing-dot"></div>
            <div class="size-2 bg-slate-400 rounded-full typing-dot"></div>
        </div>
    `;
    container.appendChild(typingEl);
    scrollToBottom();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });
        const data = await res.json();

        // Remove typing indicator
        document.getElementById('typing-indicator')?.remove();

        const result = data.data || {};
        const answer = result.answer || 'שגיאה בעיבוד השאלה';
        const sql = result.sql;

        const aiBubble = document.createElement('div');
        aiBubble.className = 'flex flex-col items-start gap-1';

        let sqlSection = '';
        if (sql) {
            sqlSection = `
                <details class="mt-2">
                    <summary class="text-[10px] text-primary cursor-pointer font-bold">הצג שאילתת SQL</summary>
                    <pre class="mt-1 text-[10px] bg-slate-200 p-2 rounded-lg overflow-x-auto direction-ltr text-left font-mono">${escapeHtml(sql)}</pre>
                </details>
            `;
        }

        aiBubble.innerHTML = `
            <div class="bg-slate-100 p-4 rounded-2xl rounded-tr-none text-sm max-w-[80%] border-r-4 border-primary">
                <div class="whitespace-pre-wrap">${escapeHtml(answer)}</div>
                ${sqlSection}
            </div>
            <span class="text-[10px] text-slate-400 mr-2">${new Date().toLocaleTimeString('he-IL', {hour: '2-digit', minute: '2-digit'})}</span>
        `;
        container.appendChild(aiBubble);

    } catch (e) {
        document.getElementById('typing-indicator')?.remove();

        const errorBubble = document.createElement('div');
        errorBubble.className = 'flex flex-col items-start gap-1';
        errorBubble.innerHTML = `
            <div class="bg-red-50 text-red-600 p-3 rounded-2xl rounded-tr-none text-sm max-w-[80%] border border-red-200">
                שגיאה בחיבור לשרת. נסה שוב.
            </div>
        `;
        container.appendChild(errorBubble);
    }

    scrollToBottom();
}

function scrollToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
