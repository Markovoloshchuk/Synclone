// Спільний клієнтський код Synclone: JWT у localStorage + fetch-хелпер.
const TOKEN_KEY = "synclone_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function logout() {
  // Stateless JWT: вихід = видалення токена на клієнті
  clearToken();
  window.location.href = "/login.html";
}

// Обгортає fetch: додає Bearer-токен, ловить 401 і перенаправляє на вхід
async function api(url, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const token = getToken();
  if (token) {
    headers["Authorization"] = "Bearer " + token;
  }
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    clearToken();
    if (!window.location.pathname.endsWith("login.html")) {
      window.location.href = "/login.html";
    }
    throw new Error("401 Unauthorized");
  }
  return response;
}

// Поточний користувач або null (анонім / протермінований токен)
async function currentUser() {
  try {
    const response = await api("/api/users/me");
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch (e) {
    return null;
  }
}

// Захист сторінки: повертає користувача або редіректить на логін
async function requireUser() {
  const user = await currentUser();
  if (!user) {
    window.location.href = "/login.html";
    return null;
  }
  return user;
}

function renderUserHeader(user) {
  const box = document.getElementById("user-box");
  if (!box) {
    return;
  }
  const roleBadge =
    user.role === "admin"
      ? '<span class="badge badge-admin">адмін</span>'
      : '<span class="badge">користувач</span>';
  const adminLink =
    user.role === "admin"
      ? '<a href="/admin.html">Адмін-панель</a>'
      : "";
  box.innerHTML =
    "<span>" +
    user.email +
    " " +
    roleBadge +
    "</span><span>" +
    adminLink +
    ' <a href="/home.html">Головна</a> <button class="btn-link" onclick="logout()">Вихід</button></span>';
}
