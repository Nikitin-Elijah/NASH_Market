const TOKEN_URL = "http://127.0.0.1:8000/users/token";

const form = document.getElementById("loginForm");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const submitBtn = document.getElementById("submitBtn");
const statusEl = document.getElementById("status");
const rememberChk = document.getElementById("remember");

function showStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.style.color = isError ? "red" : "green";
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  showStatus("");
  submitBtn.disabled = true;

  const username = usernameInput.value.trim();
  const password = passwordInput.value;

  if (!username || !password) {
    showStatus("Введите email и пароль.", true);
    submitBtn.disabled = false;
    return;
  }

  try {
    const resp = await fetch(TOKEN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username,
        password
      })
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || `Ошибка ${resp.status}`);
    }

    const data = await resp.json();
    if (!data.access_token) {
      throw new Error("Нет access_token в ответе");
    }

    localStorage.setItem("access_token", data.access_token);

    if (rememberChk.checked && data.refresh_token) {
      localStorage.setItem("refresh_token", data.refresh_token);
    } else {
      localStorage.removeItem("refresh_token");
    }

    showStatus("Успешный вход!");

    // ⚡ редирект на главную
    window.location.href = "index.html";

  } catch (err) {
    console.error("Ошибка авторизации:", err);
    showStatus(err.message, true);
  } finally {
    submitBtn.disabled = false;
  }
});
