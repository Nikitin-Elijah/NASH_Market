import { useContext } from 'react';
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../methods/ApiMethods.jsx';


const MyProductButton = () => {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const handleMyProducts = () => {
    navigate("/my-products")
  }
  if (!user) return (
    <></>
  )

  return (
    <button
      onClick={handleMyProducts}
      className="btn btn-outline-primary rounded-pill"
    >
      Мои товары
    </button>
  )
}



export default MyProductButton;