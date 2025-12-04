import React from "react";
import {useNavigate} from "react-router-dom";

const FavoriteProductsButton = () => {
  const navigate = useNavigate();
  const handleFavoriteProducts = () => {
    navigate("/favorite-products");
  };

  return (
    <button onClick={handleFavoriteProducts} className="">
      Избранное
    </button>
  );
};

export default FavoriteProductsButton;
