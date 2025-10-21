import { useContext } from 'react';
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../ApiMethods';


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
      className="btn btn-outline-primary d-flex align-items-center gap-1 m-2 rounded-pill"
    >
      Добавить товар
    </button>
  )
}



export default AddButton;