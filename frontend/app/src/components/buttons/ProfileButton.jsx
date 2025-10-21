import { useContext } from 'react';
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../methods/ApiMethods.jsx';


const ProfileButton = () => {
  const navigate = useNavigate();
  const { isTokenValid } = useContext(AuthContext);
  const { user } = useContext(AuthContext);
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
    <button
      onClick={handleProfile} 
      className="btn btn-outline-primary d-flex align-items-center justify-content-center rounded-pill"
    >
      <img src={user.photo_url || '/blue-avatar.png'} alt="" className='rounded mx-auto' 
        style={{
                width: '25px',
                height: '25px',
                borderRadius: '50%',
                objectFit: 'cover',
                display: 'block'
              }}/>
      <span>{user.username}</span>
    </button>
  )
}



export default ProfileButton;