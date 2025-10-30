import React, {useContext, useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods.jsx";
import Search from "./Search.jsx";
import Menu from "./Menu.jsx";

export default function Header() {
  const {isTokenValid, logout, user} = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isTokenValid()) logout();
  }, [user]);

  const handleLogin = () => navigate("/login");
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);
  if (!user)
    return (
      <>
        {isMobile ? (
          <>
            <header className="w-100 container-bg-light">
              <div className="d-flex justify-content-between align-items-center">
                <h3
                  onClick={() => navigate("/")}
                  className="d-flex align-items-center m-2"
                  style={{cursor: "pointer"}}
                >
                  <span className="d-none d-sm-inline">NASH Market</span>
                  <span className="d-inline d-sm-none">
                    NASH
                    <br />
                    Market
                  </span>
                </h3>
                <button onClick={handleLogin} className="m-2">
                  Войти
                </button>
              </div>
              <div className="m-2"></div>
            </header>
            <Search />
          </>
        ) : (
          <>
            <header className="w-100 container-bg-light">
              <div className="d-flex justify-content-between align-items-center">
                <div className="brand-section">
                  <h3
                    onClick={() => navigate("/")}
                    className="d-flex align-items-center m-2"
                    style={{cursor: "pointer"}}
                  >
                    <span className="d-none d-sm-inline">NASH Market</span>
                    <span className="d-inline d-sm-none">
                      NASH
                      <br />
                      Market
                    </span>
                  </h3>
                </div>
                <div className="flex-fill mx-3">
                  <Search />
                </div>
                <div className="actions-section">
                  <button onClick={handleLogin} className="m-2">
                    Войти
                  </button>
                </div>
              </div>
              <div className="m-2"></div>
            </header>
          </>
        )}
      </>
    );

  return (
    <>
      {isMobile ? (
        <>
          <header className="w-100">
            <div className="d-flex justify-content-between align-items-center">
              <h3
                onClick={() => navigate("/")}
                className="d-flex align-items-center m-2"
                style={{cursor: "pointer"}}
              >
                <span className="d-none d-sm-inline">NASH Market</span>
                <span className="d-inline d-sm-none">
                  NASH
                  <br />
                  Market
                </span>
              </h3>
              <div className="m-2">
                <Menu />
              </div>
            </div>
            <div></div>
            <div className="m-2"></div>
          </header>
          <Search />
        </>
      ) : (
        <>
          <header className="w-100">
            <div className="d-flex justify-content-between align-items-center">
              <div className="brand-section">
                <h3
                  onClick={() => navigate("/")}
                  className="d-flex align-items-center m-2"
                  style={{cursor: "pointer"}}
                >
                  <span className="d-none d-sm-inline">NASH Market</span>
                  <span className="d-inline d-sm-none">
                    NASH
                    <br />
                    Market
                  </span>
                </h3>
              </div>

              <div className="flex-fill mx-3">
                <Search />
              </div>

              <div className="actions-section m-2">
                <Menu />
              </div>
            </div>
            <div className="m-2"></div>
          </header>
        </>
      )}
    </>
  );
}
