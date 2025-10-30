import React, {useContext, useState} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods.jsx";
import Header from "../layouts/Header.jsx";

const Settings = () => {
  const {user, logout, uploadPhoto, setUser} = useContext(AuthContext);
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [username_tg, setUsernameTg] = useState("");
  const [photoUrl, setPhotoUrl] = useState("");

  const handleLogout = () => {
    logout();
    setUser(null);
    navigate("/");
  };
  React.useEffect(() => {
    if (!user) {
      navigate("/login");
      setUser(null);
      return;
    }
    setUsername(user.username);
    setUsernameTg(user.tg_username);
    setPhotoUrl(user.photo_url || "/blue-avatar.png");
  }, [user, navigate]);

  return (
    <div>
      <Header />
      <div className="d-flex justify-content-center">
        <div className="d-flex flex-column align-items-center m-5 w-50 container-card-page">
          <h1 className="text fs-1 mt-3">Настройки</h1>
          <div></div>

          <div className="w-50 d-flex justify-content-center align-items-center">
            <button className="btn-danger" onClick={handleLogout}>
              Выйти
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
