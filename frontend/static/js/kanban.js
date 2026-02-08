document.addEventListener('DOMContentLoaded', () => {
    const columns = document.querySelectorAll('[id^="column-"]');

    columns.forEach(column => {
        new Sortable(column, {
            group: 'kanban',
            animation: 200,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            handle: '.cursor-grab',
            filter: 'button',
            onEnd: async (evt) => {
                const taskId = evt.item.dataset.taskId;
                const newStatus = evt.to.dataset.status;
                const newIndex = evt.newIndex;

                try {
                    await fetch(`/api/tasks/${taskId}/status`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            status: newStatus,
                            position: newIndex,
                        }),
                    });
                } catch (e) {
                    // Silently fail — task stays in new position visually
                }
            },
        });
    });
});
