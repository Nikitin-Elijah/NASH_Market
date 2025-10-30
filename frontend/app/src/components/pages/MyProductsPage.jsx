import React from 'react'
import Header from '../layouts/Header.jsx';
import MyProductsList from '../methods/MyProductsList'


const MyProducts = () => {
    return (
        <div>
            <Header /> 
            <MyProductsList />
        </div>

    )
}

export default MyProducts