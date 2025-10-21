import React from "react";
import { useNavigate } from "react-router-dom";
import 'bootstrap-icons/font/bootstrap-icons.css';

const HomeButton = () => {
    const navigate = useNavigate();
    
    const handleBack = () => {
        navigate(-1)
    };

    return (
        <div className="d-flex justify-content-between">
             <button className="btn btn-primary m-3 bi-arrow-left" onClick={handleBack}>  
            </button>
        </div>
    )
}

export default HomeButton
