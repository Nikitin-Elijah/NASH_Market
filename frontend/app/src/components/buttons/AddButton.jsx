import React from "react";
import { useNavigate } from "react-router-dom";

const AddButton = () => {
  const navigate = useNavigate();
  const handleAddProduct = () => {
    navigate("/add-product");
  };

  return (
    <div>
      <button onClick={handleAddProduct} className="">
        Добавить товар
      </button>
    </div>
  );
};

export default AddButton;
