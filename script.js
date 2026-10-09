// プロンプトのコピーボタン
document.querySelectorAll(".copy-btn").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var target = document.getElementById(btn.dataset.copy);
    if (!target) return;
    navigator.clipboard.writeText(target.textContent).then(function () {
      btn.textContent = "✅ コピーしました";
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = "📋 コピー";
        btn.classList.remove("copied");
      }, 2000);
    });
  });
});

// 「できたかな？」チェックの保存（ページを閉じても残る）
document.querySelectorAll('input[type="checkbox"][data-save]').forEach(function (box) {
  var key = "papa-guide-" + box.dataset.save;
  box.checked = localStorage.getItem(key) === "1";
  box.addEventListener("change", function () {
    localStorage.setItem(key, box.checked ? "1" : "0");
  });
});
