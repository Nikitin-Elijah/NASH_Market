import React, {useContext, useEffect, useState, useRef} from "react";
import {useNavigate, useLocation} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods.jsx";
import Search from "./Search.jsx";
import Menu from "./Menu.jsx";

export default function Header() {
  const {isTokenValid, logout, user} = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  const headerRef = useRef(null);
  const isMailboxPage = location.pathname === "/mailbox";

  useEffect(() => {
    if (!isTokenValid()) logout();
  }, [user]);

  const handleLogin = () => navigate("/login");
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1410);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1410);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Вычисляем высоту header и позиционируем Search
  useEffect(() => {
    if (isMobile && headerRef.current) {
      const updateSearchPosition = () => {
        const headerHeight = headerRef.current?.offsetHeight || 0;
        const searchContainer = document.querySelector(
          "header + .search-container"
        );
        if (searchContainer) {
          const searchHeight = searchContainer.offsetHeight || 0;
          searchContainer.style.top = `${headerHeight}px`;

          // Обновляем отступ для контента
          const pageContainer = searchContainer.parentElement;
          if (pageContainer) {
            pageContainer.style.paddingTop = `${headerHeight + searchHeight}px`;
          }
        }
      };

      // Небольшая задержка для правильного вычисления высоты после рендера
      const timeoutId = setTimeout(updateSearchPosition, 0);
      window.addEventListener("resize", updateSearchPosition);
      return () => {
        clearTimeout(timeoutId);
        window.removeEventListener("resize", updateSearchPosition);
      };
    }
  }, [isMobile, user]);
  if (!user)
    return (
      <>
        {isMobile ? (
          <>
            <header ref={headerRef} className="w-100 container-bg-light">
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
            {!isMailboxPage && <Search />}
          </>
        ) : (
          <>
            <header ref={headerRef} className="w-100 container-bg-light">
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
                {!isMailboxPage && (
                  <div className="flex-fill mx-3">
                    <Search />
                  </div>
                )}
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
          <header ref={headerRef} className="w-100">
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
          {!isMailboxPage && <Search />}
        </>
      ) : (
        <>
          <header ref={headerRef} className="w-100">
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

              {!isMailboxPage && (
                <div className="flex-fill mx-3">
                  <Search />
                </div>
              )}

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
