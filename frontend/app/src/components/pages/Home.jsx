import React from 'react'
import ProfileButton from '../buttons/ProfileButton'
import AddButton from '../buttons/AddButton';
import MyProductButton from '../buttons/MyProductButton';
import ProductList from '../ProductsList'
const name = 'NASH Market'


const Home = () => {
    return (
        <div>
            <div className='d-flex justify-content-between align-items-center shadow-sm'>
                <span className='fw-bold fs-2 text-primary m-3'>{name}</span>
                <div className='d-flex'>
                    <AddButton />
                    <MyProductButton />
                    <ProfileButton />
                </div>
            </div>
            <div className='d-flex flex-column align-items-center m-4'>
                <ProductList />
            </div>                           
        </div>
    )
}

export default Home