import React from 'react'
import HomeButton from '../buttons/HomeButton'
import MyProductsList from '../MyProductsList'


const MyProducts = () => {
    return (
        <div>
            <HomeButton/> 
            <div className='d-flex flex-column align-items-center m-4'>
                <span className='fs-4'>Мои товары</span>                    
            </div>
            <MyProductsList />
                
        </div>

    )
}

export default MyProducts