import React from "react";
import {useNavigate} from "react-router-dom";

const MailBoxButton = () => {
  const navigate = useNavigate();
  const handleMailBox = () => {
    navigate("/mailbox");
  };

  return (
    <button onClick={handleMailBox} className="">
      Почта
    </button>
  );
};

export default MailBoxButton;
