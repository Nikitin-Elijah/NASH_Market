import React, {useContext, useState} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods";
import Header from "../layouts/Header.jsx";
import MyProductsList from "../methods/MyProductsList.jsx";

const MyProfilePage = () => {
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

  const handlePhotoChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        uploadPhoto(file)
          .then((url) => {
            setPhotoUrl(url);
          })
          .catch(() => {
            console.error("Ошибка загрузки фото");
          });
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div>
      <Header />
      <div className="">
        <div className="w-100 d-flex flex-row justify-content-start">
          <div>
            <img
              src={photoUrl}
              alt={username || "avatar"}
              style={{
                width: "100px",
                height: "100px",
                borderRadius: "50%",
                objectFit: "cover",
                display: "block",
              }}
              className="m-2"
            />
          </div>
          <div className="d-flex flex-column justify-content-center m-2">
            <h5 className="text fs-3">{username}</h5>
            <span className="text fs-5">@{username}</span>
          </div>
        </div>
        <div className="w-50 d-flex justify-content-center align-items-center">
          <button className="btn-danger" onClick={handleLogout}>
            Выйти
          </button>
        </div>
        <div>
          <MyProductsList />
        </div>
      </div>
    </div>
  );
};

export default MyProfilePage;
