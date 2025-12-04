import React, {useState, useEffect} from "react";
import ProfileButton from "../buttons/ProfileButton.jsx";
import Burger from "./Burger.jsx";
import AddButton from "../buttons/AddButton.jsx";
import SettingsButton from "../buttons/SettingsButton.jsx";
import FavoriteProductsButton from "../buttons/FavoriteProductsButton.jsx";
import MailBoxButton from "../buttons/MailBoxButton.jsx";

export default function Menu() {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1000);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1000);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div>
      {isMobile ? (
        <>
          <Burger />
        </>
      ) : (
        <>
          <div className="d-flex gap-2">
            <AddButton />
            <SettingsButton />
            <FavoriteProductsButton />
            <MailBoxButton />
            <ProfileButton />
          </div>
        </>
      )}
    </div>
  );
}
