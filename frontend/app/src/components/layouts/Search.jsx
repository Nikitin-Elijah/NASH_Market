import React, {useContext, useState, useEffect} from "react";

export default function Search() {
  const [query, setQuery] = useState("");

  const handleChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSearch = () => {
    console.log("Поиск:", query);
  };
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div className="search-container m-2">
      <input type="text" className="search-input" placeholder="Поиск" />
    </div>
  );
}
