import React, { useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ProfileButton from "../buttons/ProfileButton";
import AddButton from "../buttons/AddButton";
import MyProductButton from "../buttons/MyProductButton";
import { AuthContext } from "../methods/ApiMethods.jsx";
import { FaBars } from "react-icons/fa";

export default function Header() {
  const { isTokenValid, logout, user } = useContext(AuthContext);
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const name = "NASH Market";

  useEffect(() => {
    if (!isTokenValid()) logout();
  }, [user]);

  const handleLogin = () => navigate("/login");

  // если пользователь не авторизован
  if (!user)
    return (
      <nav
        className="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm px-3 py-2"
        style={{ height: "8vh" }}
      >
        <div className="container-fluid d-flex justify-content-between align-items-center">
          <h1
            onClick={() => navigate("/")}
            className="h5 m-0 text-primary fw-semibold"
            style={{ cursor: "pointer" }}
          >
            {name}
          </h1>

          <button onClick={handleLogin} className="btn btn-outline-primary">
            Войти
          </button>
        </div>
      </nav>
    );

  return (
    <nav
      className="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm px-3 py-2 position-relative"
      style={{ height: "10vh" }}
    >
      <div className="container-fluid d-flex justify-content-between align-items-center">
        {/* Логотип */}
        <h1
          onClick={() => navigate("/")}
          className="h5 m-0 text-primary fw-semibold"
          style={{ cursor: "pointer" }}
        >
          {name}
        </h1>

        {/* Кнопки справа для больших экранов */}
        <div className="d-none d-lg-flex align-items-center gap-2">
          <AddButton />
          <MyProductButton />
          <ProfileButton />
        </div>

        {/* Кнопка меню для маленьких экранов */}
        <div className="d-lg-none">
          <button
            className="btn btn-outline-primary"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <FaBars size={20} />
          </button>
        </div>
      </div>

      {/* Боковое меню (offcanvas) */}
      {menuOpen && (
        <div
          className="position-absolute top-0 end-0 bg-white shadow-lg p-4"
          style={{
            width: "250px",
            height: "100vh",
            zIndex: 1050,
            transition: "transform 0.3s ease-in-out",
          }}
        >
          <button
            className="btn-close mb-3"
            onClick={() => setMenuOpen(false)}
          ></button>

          <div className="d-flex flex-column gap-3">
            <ProfileButton />
            <MyProductButton />
            <AddButton />
          </div>
        </div>
      )}
    </nav>
  );
}
