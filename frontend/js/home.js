const authBlock = document.getElementById("authBlock");
const token = localStorage.getItem("access_token");
const PROFILE_URL = "http://127.0.0.1:8000/users/me";

const userActions = document.getElementById("userActions");
const addProductBtn = document.getElementById("addProductBtn");
const myProductsBtn = document.getElementById("myProductsBtn");

let allProducts = []; // сохраняем все товары для фильтрации
let currentUser = null;

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
  } catch {
    return null;
  }
}

async function loadProfile() {
  try {
    const resp = await fetch(PROFILE_URL, {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!resp.ok) throw new Error("unauthorized");

    const data = await resp.json();
    renderProfile(data);
  } catch {
    renderLogin();
  }
}

function renderLogin() {
  const loginBtn = document.createElement("button");
  loginBtn.textContent = "Войти";
  loginBtn.className = "primary";
  loginBtn.addEventListener("click", () => {
    window.location.href = "login.html";
  });
  authBlock.innerHTML = "";
  authBlock.appendChild(loginBtn);
}

function renderProfile(data) {

  currentUser = data;
  const username = data.username || "Профиль";
  const photo = data.photo_url || "images/default-avatar.jpg";

  const profileDiv = document.createElement("div");
  profileDiv.className = "mini-profile";
  profileDiv.innerHTML = `
    <img src="${photo}" class="mini-avatar" alt="аватар"/>
    <span>${username}</span>
  `;
  profileDiv.addEventListener("click", () => {
    window.location.href = "user.html";
  });

  authBlock.innerHTML = "";
  authBlock.appendChild(profileDiv);

  // показать кнопки действий
  if (userActions) userActions.hidden = false;

  if (addProductBtn) {
    addProductBtn.addEventListener("click", () => {
      window.location.href = "create-product.html";
    });
  }

  if (myProductsBtn) {
    myProductsBtn.addEventListener("click", () => {
      window.location.href = "my-products.html";
    });
  }
}

if (!token) {
  renderLogin();
} else {
  const payload = parseJwt(token);
  if (!payload || (payload.exp && Date.now() >= payload.exp * 1000)) {
    renderLogin();
  } else {
    loadProfile();
  }
}

const PRODUCTS_URL = "http://127.0.0.1:8000/products/";
const productsList = document.getElementById("productsList");

async function loadProducts() {
  try {
    const resp = await fetch(PRODUCTS_URL);
    if (!resp.ok) throw new Error("Не удалось загрузить товары");

    const products = await resp.json();
    allProducts = products;
    renderProducts(products);
  } catch (e) {
    console.error(e);
    productsList.innerHTML = "<p>Не удалось загрузить товары</p>";
  }
}

function renderProducts(products) {
  productsList.innerHTML = "";
  if (!products || products.length === 0) {
    productsList.innerHTML = "<p>Нет товаров для отображения</p>";
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
      </div>
    `;
    productsList.appendChild(card);
  });
}

// загрузка товаров при старте
loadProducts();
