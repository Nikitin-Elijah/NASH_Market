const token = localStorage.getItem("access_token");
const form = document.getElementById("productForm");
const statusEl = document.getElementById("status");

const prodTitle = document.getElementById("prodTitle");
const prodDesc = document.getElementById("prodDesc");
const prodPrice = document.getElementById("prodPrice");
const prodPhoto = document.getElementById("prodPhoto");
const productCard = document.getElementById("productCard");

const photoInput = document.getElementById("photo");
const previewImg = document.getElementById("previewImg");

// API endpoint для создания товара
const CREATE_URL = "http://127.0.0.1:8000/products"; // подстрой под свой бэк

// 👉 Проверка токена сразу
if (!token) {
  window.location.href = "login.html";
}

// 🔹 показываем превью при выборе файла
photoInput.addEventListener("change", () => {
  const file = photoInput.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    previewImg.src = "images/default-product.jpg";
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const price = parseFloat(document.getElementById("price").value);
  const photoFile = photoInput.files[0];

  const formData = new FormData();
  formData.append("name", title);
  formData.append("description", description);
  formData.append("price", price);
  if (photoFile) formData.append("image", photoFile);

  try {
    statusEl.textContent = "Создаём товар...";
    const resp = await fetch(CREATE_URL, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });

    if (resp.status === 401) {
      // токен невалиден → отправляем на login
      localStorage.removeItem("access_token");
      window.location.href = "login.html";
      return;
    }

    if (!resp.ok) throw new Error("Ошибка создания товара");

    const data = await resp.json();

    prodTitle.textContent = data.name;
    prodDesc.textContent = data.description;
    prodPrice.textContent = `Цена: ${data.price} ₽`;
    prodPhoto.src = data.image_url || previewImg.src;
    productCard.hidden = false;
    statusEl.textContent = "Товар успешно создан!";
  } catch (e) {
    statusEl.textContent = "Ошибка: " + e.message;
  }
});
