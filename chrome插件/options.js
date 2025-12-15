document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save').addEventListener('click', saveOptions);

function saveOptions() {
  const apiUrl = document.getElementById('apiUrl').value;
  const apiKey = document.getElementById('apiKey').value;
  const modelName = document.getElementById('modelName').value;

  chrome.storage.sync.set(
    { apiUrl, apiKey, modelName },
    () => {
      const status = document.getElementById('status');
      status.textContent = '设置已保存！';
      setTimeout(() => { status.textContent = ''; }, 2000);
    }
  );
}

function restoreOptions() {
  chrome.storage.sync.get(
    { 
      apiUrl: 'https://api.openai.com/v1', 
      apiKey: '',
      modelName: 'gpt-3.5-turbo'
    },
    (items) => {
      document.getElementById('apiUrl').value = items.apiUrl;
      document.getElementById('apiKey').value = items.apiKey;
      document.getElementById('modelName').value = items.modelName;
    }
  );
}
