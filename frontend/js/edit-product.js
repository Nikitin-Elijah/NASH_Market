const token = localStorage.getItem("access_token");
if (!token) {
  window.location.href = "login.html";
}

const urlParams = new URLSearchParams(window.location.search);
const productId = urlParams.get("id");

if (!productId) {
  alert("ID товара не указан");
  window.location.href = "my-products.html";
}

const PRODUCT_URL = `http://127.0.0.1:8000/products/${productId}`;
const form = document.getElementById("editForm");
const statusEl = document.getElementById("status");

const titleInput = document.getElementById("title");
const descInput = document.getElementById("description");
const priceInput = document.getElementById("price");
const photoInput = document.getElementById("photo");
const previewImg = document.getElementById("previewImg");

// 🔹 загрузка текущих данных
async function loadProduct() {
  try {
    const resp = await fetch(PRODUCT_URL, {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (resp.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "login.html";
      return;
    }

    if (!resp.ok) throw new Error("Ошибка загрузки товара");

    const data = await resp.json();
    titleInput.value = data.name;
    descInput.value = data.description;
    priceInput.value = data.price;
    previewImg.src = data.image_url || "images/default-product.jpg";
  } catch (e) {
    statusEl.textContent = "Ошибка: " + e.message;
  }
}

photoInput.addEventListener("change", () => {
  const file = photoInput.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
});

// 🔹 сохранение изменений
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData();
  formData.append("name", titleInput.value.trim());
  formData.append("description", descInput.value.trim());
  formData.append("price", parseFloat(priceInput.value));
  if (photoInput.files[0]) {
    formData.append("image", photoInput.files[0]);
  }

  try {
    statusEl.textContent = "Сохраняем изменения...";
    const resp = await fetch(PRODUCT_URL, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });

    if (resp.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "login.html";
      return;
    }

    if (!resp.ok) throw new Error("Ошибка при сохранении");

    statusEl.textContent = "Изменения сохранены!";
    setTimeout(() => window.location.href = "my-products.html", 1200);
  } catch (e) {
    statusEl.textContent = "Ошибка: " + e.message;
  }
});

loadProduct();
