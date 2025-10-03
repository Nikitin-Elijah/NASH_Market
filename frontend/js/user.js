const token = localStorage.getItem("access_token");
const usernameEl = document.getElementById("username");
const emailEl = document.getElementById("email");
const avatarEl = document.getElementById("avatar");
const editBtn = document.getElementById("editPhoto");
const fileInput = document.getElementById("fileInput");
const logoutBtn = document.getElementById("logout");
const statusEl = document.getElementById("status");
const addBtn = document.getElementById("addProductBtn");

const goHomeBtn = document.getElementById("goHome");

if (goHomeBtn) {
  goHomeBtn.addEventListener("click", () => {
    window.location.href = "index.html";
  });
}

// 👉 эндпоинты API
const UPLOAD_URL = "http://127.0.0.1:8000/users/upload-photo";
const PROFILE_URL = "http://127.0.0.1:8000/users/me";

// 👉 нет токена → сразу редирект
if (!token) {
  window.location.href = "login.html";
}

function parseJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

const payload = parseJwt(token);

// 👉 проверка срока жизни токена
if (!payload || (payload.exp && Date.now() >= payload.exp * 1000)) {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "login.html";
}

// Показываем данные
if (payload) {
  usernameEl.textContent = payload.username || "Без имени";
  emailEl.textContent = payload.sub || payload.email || "";
}

// 🔹 Загружаем профиль
async function loadProfile() {
  try {
    const resp = await fetch(PROFILE_URL, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (resp.status === 401) {
      // токен больше не валиден
      logoutAndRedirect();
      return;
    }
    if (resp.ok) {
      const data = await resp.json();
      if (data.photo_url) {
        avatarEl.src = data.photo_url;
      }
    }
  } catch (e) {
    console.warn("Не удалось загрузить профиль", e);
  }
}
loadProfile();

// 🔹 Выбор фото
editBtn.addEventListener("click", () => {
  fileInput.click();
});

// 🔹 Загрузка фото
fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  // Предпросмотр фото локально
  const previewUrl = URL.createObjectURL(file);
  avatarEl.src = previewUrl;

  const formData = new FormData();
  formData.append("photo", file);

  try {
    statusEl.textContent = "Загружаем фото...";
    const resp = await fetch(UPLOAD_URL, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });

    if (resp.status === 401) {
      logoutAndRedirect();
      return;
    }

    if (!resp.ok) throw new Error("Ошибка загрузки фото");

    const data = await resp.json();
    if (data.photo_url) {
      avatarEl.src = data.photo_url; // заменяем превью на URL сервера
    }
    statusEl.textContent = "Фото обновлено!";
  } catch (e) {
    statusEl.textContent = "Ошибка: " + e.message;
  }
});

// 🔹 Выход
logoutBtn.addEventListener("click", logoutAndRedirect);

function logoutAndRedirect() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "login.html";
}

addBtn.addEventListener("click", () => {
  window.location.href = "create-product.html";
});
