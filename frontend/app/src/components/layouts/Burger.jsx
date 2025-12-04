import React, {useState, useEffect} from "react";
import ProfileButton from "../buttons/ProfileButton.jsx";
import AddButton from "../buttons/AddButton.jsx";
import SettingsButton from "../buttons/SettingsButton.jsx";
import FavoriteProductsButton from "../buttons/FavoriteProductsButton.jsx";
import MailBoxButton from "../buttons/MailBoxButton.jsx";
export default function Burger() {
  const [menuOpen, setMenuOpen] = useState(false);
  const toggleMenu = () => setMenuOpen(!menuOpen);
  const closeMenu = () => setMenuOpen(false);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        menuOpen &&
        !event.target.closest(".side-menu") &&
        !event.target.closest(".burger")
      ) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  return (
    <div>
      <label className={`burger ${menuOpen ? "active" : ""}`}>
        <input type="checkbox" checked={menuOpen} onChange={toggleMenu} />
        <span></span>
        <span></span>
        <span></span>
      </label>

      <div
        className={`overlay ${menuOpen ? "show" : ""}`}
        onClick={closeMenu}
      ></div>

      <ul className={`side-menu ${menuOpen ? "open" : ""}`}>
        <li className="menu-item">
          <ProfileButton />
        </li>
        <li className="menu-item">
          <FavoriteProductsButton />
        </li>
        <li className="menu-item">
          <MailBoxButton />
        </li>
        <li className="menu-item">
          <SettingsButton />
        </li>
        <li className="menu-item">
          <AddButton />
        </li>
      </ul>
    </div>
  );
}
