const fileInput = document.getElementById('jsonFile');
const submitBtn = document.getElementById('submitBtn');
const resultDiv = document.getElementById('result');
const spinner = document.getElementById('spinner');
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
  resultDiv.innerHTML = '';
  spinner.style.display = 'block';
  fetch('/api/validate-summary-stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jsonData)
  })
  .then(response => {
    const reader = response.body.getReader();
    let result = '';
    function read() {
      return reader.read().then(({ done, value }) => {
        if (done) {
          spinner.style.display = 'none';
          return;
        }
        result += new TextDecoder().decode(value);
        resultDiv.innerHTML = marked.parse(result);
        return read();
      });
    }
    return read();
  })
  .catch(err => {
    spinner.style.display = 'none';
    resultDiv.innerHTML = '<span class="error">Error: ' + err.message + '</span>';
  });
});