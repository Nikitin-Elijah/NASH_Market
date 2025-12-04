import {useContext} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods.jsx";

const ProfileButton = () => {
  const {user, isTokenValid} = useContext(AuthContext);
  const navigate = useNavigate();
  const handleProfile = async () => {
    const valid = await isTokenValid();
    if (!valid) {
      navigate("/login");
      return;
    } else {
      navigate("/profile");
    }
  };
  return (
    <button className="d-flex align-items-center gap-2" onClick={handleProfile}>
      <img
        alt={user?.username || "Profile"}
        onClick={handleProfile}
        title={user?.username}
        src={user?.photo_url || "/blue-avatar.png"}
        className="d-flex align-items-center justify-content-center rounded-circle text-white border-0"
        style={{
          width: "25px",
          height: "25px",
          cursor: "pointer",
        }}
      ></img>
      <span>{user?.username}</span>
    </button>
  );
};

export default ProfileButton;
