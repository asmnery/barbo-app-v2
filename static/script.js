document.addEventListener('DOMContentLoaded', function() {
    const dataInput = document.getElementById('data');
    
    function formatDate() {
        const date = new Date(dataInput.value);
        if (!isNaN(date)) {
            
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            dataInput.value = `${day}/${month}/${year}`;
        }
    }
    
    dataInput.addEventListener('change', formatDate);
});