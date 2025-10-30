import React from "react";
import { useNavigate } from "react-router-dom";

const SettingsButton = () => {
  const navigate = useNavigate();
  const handleClick = () => {
    navigate("/settings");
  };

  return (
    <div>
      <button onClick={handleClick} className="">
        Настройки
      </button>
    </div>
  );
};

export default SettingsButton;
