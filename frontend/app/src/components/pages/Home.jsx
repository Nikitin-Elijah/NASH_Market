import React from 'react'
import { useNavigate } from "react-router-dom";
import ProfileButton from '../buttons/ProfileButton'
import ProductList from '../ProductsList'
const name = 'NASH Market'


const Home = () => {
    const navigate = useNavigate();

    const handleAddProduct = () => {
        navigate("/add-product")
    }
    
    const handleMyProducts = () => {
        navigate("/my-products")
    }
    return (
        <div>
            <div className='d-flex justify-content-between align-items-center shadow-sm'>
                <span className='fw-bold fs-2 text-primary m-3'>{name}</span>
                <div className='d-flex'>
                    <button className='btn btn-light m-2 btn-outline-secondary'
                    onClick={handleAddProduct}>Добавить товары</button>
                    <button className='btn btn-light m-2 btn-outline-secondary'
                    onClick={handleMyProducts}>Мои товары</button>
                    <ProfileButton />
                </div>
            </div>
            <div className='d-flex flex-column align-items-center m-2'>
                <span className='fs-4 m-3'>Товары</span>
                <ProductList />
            </div>                           
        </div>
    )
}

export default Home