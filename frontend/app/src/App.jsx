import { BrowserRouter, Routes, Route } from "react-router-dom";

import LoginPage from "./components/pages/LoginPage";
import MyProducts from "./components/pages/MyProductsPage";
import AddProduct from "./components/pages/AddProductPage";
import Home from "./components/pages/Home";
import MyProfilePage from "./components/pages/MyProfilePage";
import PrivateRoute from './components/PrivateRoute';
import { AuthProvider } from './components/ApiMethods';
import EditProductPage from "./components/pages/EditProductPage";




function App() {
  return (
    <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/add-product" element={<AddProduct />} />
            <Route path="/my-products" element={<MyProducts />} />
            <Route path="/profile" element={<MyProfilePage />} />
            <Route path="/edit-product/:id" element={<EditProductPage />} />
          </Routes>
        </BrowserRouter>
    </AuthProvider>
  );
}

export default App