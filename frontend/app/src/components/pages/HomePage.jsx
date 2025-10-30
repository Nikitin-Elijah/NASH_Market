import React from 'react'
import ProductList from '../methods/ProductsList'
import Header from '../layouts/Header';


const Home = () => {
    return (
        <div>
            <Header />
            <ProductList />
        </div>
    )
}

export default Home