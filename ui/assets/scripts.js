// Summary Refinement Component Scripts

document.addEventListener('DOMContentLoaded', function() {
    // Word count functionality
    const summaryEditor = document.getElementById('summary-editor');
    const wordCountValue = document.getElementById('word-count-value');
    
    if (summaryEditor && wordCountValue) {
        const updateWordCount = () => {
            const text = summaryEditor.value;
            const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
            wordCountValue.textContent = wordCount;
        };
        
        summaryEditor.addEventListener('input', updateWordCount);
        updateWordCount(); // Initial count
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter to confirm final draft
        if (e.ctrlKey && e.key === 'Enter') {
            const confirmBtn = document.getElementById('confirm-btn');
            if (confirmBtn && !confirmBtn.disabled) {
                confirmBtn.click();
            }
        }
        
        // Ctrl+Shift+Enter to apply refinement
        if (e.ctrlKey && e.shiftKey && e.key === 'Enter') {
            const refineBtn = document.getElementById('refine-btn');
            if (refineBtn && !refineBtn.disabled) {
                refineBtn.click();
            }
        }
    });

    // Auto-focus next input after actions
    const setupAutoFocus = () => {
        const confirmBtn = document.getElementById('confirm-btn');
        const proceedBtn = document.getElementById('proceed-btn');
        
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                setTimeout(() => {
                    if (proceedBtn && proceedBtn.style.display !== 'none') {
                        proceedBtn.focus();
                    }
                }, 100);
            });
        }
    };
    
    setupAutoFocus();
}); 