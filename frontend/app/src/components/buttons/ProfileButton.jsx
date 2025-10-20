import { useContext } from 'react';
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../ApiMethods';


const ProfileButton = () => {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const handleLogin = () => {
    navigate("/login")
  }
  const handleProfile = () => {
    navigate("/profile")
  }
  if (!user) return (
    (
    <button
      onClick={handleLogin} 
      className="btn btn-primary m-3"
    >
      Войти
    </button>
  )
  )

  return (
    <button
      onClick={handleProfile} 
      className="btn btn-outline-primary d-flex align-items-center gap-1 m-2 rounded-pill"
    >
      <img src={user.photo_url} alt="" className='rounded' 
        style={{
                width: '30px',
                height: '30px',
                borderRadius: '50%',
                objectFit: 'cover',
                display: 'block'
              }}/>
      <span>{user.username}</span>
    </button>
  )
}



export default ProfileButton;