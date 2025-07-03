const fileInput = document.getElementById('jsonFile');
const submitBtn = document.getElementById('submitBtn');
const resultDiv = document.getElementById('result');
let jsonData = null;

fileInput.addEventListener('change', function() {
  const file = fileInput.files[0];
  if (!file) {
    submitBtn.disabled = true;
    resultDiv.innerHTML = '';
    return;
  }
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      jsonData = JSON.parse(e.target.result);
      submitBtn.disabled = false;
      resultDiv.innerHTML = '';
    } catch (err) {
      resultDiv.innerHTML = '<span class="error">Invalid JSON file.</span>';
      submitBtn.disabled = true;
    }
  };
  reader.readAsText(file);
});

submitBtn.addEventListener('click', function() {
  if (!jsonData) return;
  resultDiv.innerHTML = 'Validating...';
  fetch('/api/validate-summary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jsonData)
  })
  .then(async response => {
    let data;
    try {
      data = await response.json();
    } catch (e) {
      throw new Error('Invalid response from server.');
    }
    if (!response.ok) {
      throw new Error(data.detail || 'Server error');
    }
    if (data.message) {
      resultDiv.innerHTML = data.message;
    } else {
      resultDiv.innerHTML = '<span class="error">No message found in server reply.</span>';
    }
  })
  .catch(err => {
    resultDiv.innerHTML = '<span class="error">Error: ' + err.message + '</span>';
  });
});