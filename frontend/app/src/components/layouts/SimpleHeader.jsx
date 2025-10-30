import React, { useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function SimpleHeader() {
  const name = "NASH Market";
  const navigate = useNavigate();

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm px-3 py-2" 
        style={{ height: "8vh" }}>
        <div className="container-fluid d-flex justify-content-between align-items-center">
            <div className="d-flex align-items-center gap-3">
            <h1
                onClick={() => navigate("/")}
                className="h5 m-0 fw-semibold"
                style={{ cursor: "pointer" }}
            >
                NASH Market
            </h1>
            </div>
        </div>
    </nav>
  );
}
