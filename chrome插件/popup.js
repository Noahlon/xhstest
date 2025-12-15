document.addEventListener('DOMContentLoaded', () => {
  const domainInput = document.getElementById('domain');
  const typeInput = document.getElementById('type');
  const hostInput = document.getElementById('host');
  const portInput = document.getElementById('port');
  const addBtn = document.getElementById('addBtn');
  const ruleList = document.getElementById('ruleList');

  // 加载并显示规则
  loadRules();

  // 添加规则
  addBtn.addEventListener('click', () => {
    const domain = domainInput.value.trim();
    const type = typeInput.value;
    const host = hostInput.value.trim();
    const port = portInput.value.trim();

    if (!domain || !host || !port) {
      alert("请填写完整信息");
      return;
    }

    const newRule = { id: Date.now(), domain, type, host, port };

    chrome.storage.local.get(['proxyRules'], (result) => {
      const rules = result.proxyRules || [];
      rules.push(newRule);
      chrome.storage.local.set({ proxyRules: rules }, () => {
        // 清空输入框
        domainInput.value = '';
        hostInput.value = '';
        portInput.value = '';
        loadRules();
      });
    });
  });

  // 渲染列表函数
  function loadRules() {
    chrome.storage.local.get(['proxyRules'], (result) => {
      const rules = result.proxyRules || [];
      ruleList.innerHTML = '';

      if (rules.length === 0) {
        ruleList.innerHTML = '<div style="color:#888; text-align:center;">暂无规则，默认直连</div>';
        return;
      }

      rules.forEach((rule, index) => {
        const div = document.createElement('div');
        div.className = 'rule-item';
        div.innerHTML = `
          <div class="rule-info">
            <strong>${rule.domain}</strong><br>
            ${rule.type} ${rule.host}:${rule.port}
          </div>
          <button class="delete-btn" data-id="${rule.id}">删除</button>
        `;
        ruleList.appendChild(div);
      });

      // 绑定删除事件
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const id = Number(e.target.getAttribute('data-id'));
          deleteRule(id);
        });
      });
    });
  }

  // 删除规则
  function deleteRule(id) {
    chrome.storage.local.get(['proxyRules'], (result) => {
      let rules = result.proxyRules || [];
      rules = rules.filter(r => r.id !== id);
      chrome.storage.local.set({ proxyRules: rules }, () => {
        loadRules();
      });
    });
  }
});
