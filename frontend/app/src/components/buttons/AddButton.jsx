import { useContext } from 'react';
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../methods/ApiMethods.jsx';


const AddButton = () => {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const handleAddProduct = () => {
    navigate("/add-product")
  }
  if (!user) return (
    <></>
  )

  return (
    <button
      onClick={handleAddProduct}
      className="btn btn-outline-primary rounded-pill"
    >
      Добавить товар
    </button>
  )
}



export default AddButton;