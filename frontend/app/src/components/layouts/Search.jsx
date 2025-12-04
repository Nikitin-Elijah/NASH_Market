import React, {useState} from "react";
import {useNavigate} from "react-router-dom";
import "bootstrap-icons/font/bootstrap-icons.css";

export default function Search() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = () => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="search-container m-2">
      <div className="search-input-wrapper">
        <input
          type="text"
          className="search-input"
          placeholder="Поиск"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button
          className="search-button"
          onClick={handleSearch}
          type="button"
          style={{
            position: "absolute",
            right: "8px",
            top: "50%",
            transform: "translateY(-50%)",
            background: "transparent",
            border: "none",
            cursor: "pointer",
            padding: "4px 8px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "inherit",
            transition: "color 0.2s ease",
            minWidth: "auto",
            maxHeight: "none",
            height: "auto",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = "var(--color-primary, #007bff)";
            e.currentTarget.style.transform = "translateY(-50%)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = "inherit";
            e.currentTarget.style.transform = "translateY(-50%)";
          }}
          onMouseDown={(e) => {
            e.currentTarget.style.transform = "translateY(-50%)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.transform = "translateY(-50%)";
          }}
        >
          <i className="bi bi-search" style={{fontSize: "18px"}}></i>
        </button>
      </div>
    </div>
  );
}
