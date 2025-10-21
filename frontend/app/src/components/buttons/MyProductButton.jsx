import { useContext } from 'react';
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../ApiMethods';


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
      className="btn btn-outline-primary d-flex align-items-center gap-1 m-2 rounded-pill"
    >
      Мои товары
    </button>
  )
}



export default MyProductButton;