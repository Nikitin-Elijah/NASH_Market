import { BrowserRouter, Routes, Route } from "react-router-dom";

import LoginPage from "./components/pages/LoginPage";
import MyProducts from "./components/pages/MyProductsPage";
import AddProduct from "./components/pages/AddProductPage";
import Home from "./components/pages/Home";
import MyProfilePage from "./components/pages/MyProfilePage";
import { AuthProvider } from './components/methods/ApiMethods';
import EditProductPage from "./components/pages/EditProductPage";
import RegisterPage from "./components/pages/RegisterPage";
import VerifyPage from "./components/pages/VerifyPage";
import PrivateRoute from "./components/methods/PrivateRoute.jsx";
import ProductPage from "./components/pages/ProductPage.jsx";




function App() {
  return (
    <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify" element={<VerifyPage />} />
            <Route path="/" element={<Home />} />
            <Route path="/product/:id" element={<ProductPage />} />
            <Route element={<PrivateRoute />}>
              <Route path="/add-product" element={<AddProduct />} />
              <Route path="/my-products" element={<MyProducts />} />
              <Route path="/profile" element={<MyProfilePage />} />
              <Route path="/edit-product/:id" element={<EditProductPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
    </AuthProvider>
  );
}

export default App