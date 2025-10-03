const token = localStorage.getItem("access_token");

if (!token) {
  window.location.href = "login.html";
} else {
  document.addEventListener("DOMContentLoaded", () => {
    const listEl = document.getElementById("myProductsList");
    const MY_PRODUCTS_URL = "http://127.0.0.1:8000/products/my";
    const PRODUCT_URL = "http://127.0.0.1:8000/products"; // базовый путь

    // 🔹 загрузка товаров
    async function loadMyProducts() {
      try {
        const resp = await fetch(MY_PRODUCTS_URL, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (resp.status === 401) {
          localStorage.removeItem("access_token");
          window.location.href = "login.html";
          return;
        }

        if (!resp.ok) throw new Error("Не удалось загрузить мои товары");

        const products = await resp.json();
        renderProducts(products);
      } catch (e) {
        console.error(e);
        listEl.innerHTML = "<p>Не удалось загрузить товары</p>";
      }
    }

    // 🔹 рендер карточек с кнопками управления
    function renderProducts(products) {
      listEl.innerHTML = "";
      if (!products || products.length === 0) {
        listEl.innerHTML = "<p>У вас пока нет товаров</p>";
        return;
      }

      products.forEach(prod => {
        const card = document.createElement("div");
        card.className = "product-card";
        card.innerHTML = `
          <img src="${prod.image_url || 'images/default-product.jpg'}" alt="${prod.name}">
          <div class="info">
            <h3>${prod.name}</h3>
            <p>${prod.description}</p>
            <div class="price">${prod.price} ₽</div>
            <div class="actions-block">
              <button class="secondary edit-btn" data-id="${prod.id}">✏️ Редактировать</button>
              <button class="secondary danger-btn delete-btn" data-id="${prod.id}">🗑 Удалить</button>
            </div>
          </div>
        `;
        listEl.appendChild(card);
      });

      // обработка редактирования
      document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const id = btn.dataset.id;
          window.location.href = `edit-product.html?id=${id}`;
        });
      });

      // обработка удаления
      document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
          const id = btn.dataset.id;
          if (confirm("Удалить этот товар?")) {
            try {
              const resp = await fetch(`${PRODUCT_URL}/${id}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${token}` }
              });

              if (resp.status === 401) {
                localStorage.removeItem("access_token");
                window.location.href = "login.html";
                return;
              }

              if (!resp.ok) throw new Error("Ошибка удаления");

              alert("Товар удалён");
              loadMyProducts(); // обновляем список
            } catch (err) {
              alert("Не удалось удалить товар");
              console.error(err);
            }
          }
        });
      });
    }

    loadMyProducts();
  });
}
