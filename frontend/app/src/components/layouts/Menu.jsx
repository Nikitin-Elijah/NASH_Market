import React, { useState, useEffect } from "react";
import ProfileButton from "../buttons/ProfileButton.jsx";
import Burger from "./Burger.jsx";
import AddButton from "../buttons/AddButton.jsx";
import SettingsButton from "../buttons/SettingsButton.jsx"

export default function Menu() {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
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
            <ProfileButton />
          </div>
        </>
      )}
    </div>
  );
}
