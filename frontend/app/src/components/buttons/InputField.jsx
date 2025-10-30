import React, { useContext, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { AuthContext } from "../methods/ApiMethods.jsx";

function InputField() {
    const { verify } = useContext(AuthContext);
    const location = useLocation();
    const data = location.state?.data || {};
    const user_id = data.user_id;
    const navigate = useNavigate();

    const [code, setCode] = useState(["", "", "", "", "", ""]);

    const handleChange = (value, index) => {
        if (!/^\d?$/.test(value)) return; 

        const newCode = [...code];
        newCode[index] = value;
        setCode(newCode);

        const inputs = document.querySelectorAll(".verification-code-input");

        if (value && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }

        if (newCode.every((v) => v !== "")) {
            const fullCode = newCode.join("");
            handleVerify(fullCode);
        }
    };

    const handleBackspace = (e, index) => {
        const inputs = document.querySelectorAll(".verification-code-input");
        if (e.key === "Backspace") {
            hiddenDangerText();
            if (code[index] === "" && index > 0) {
                inputs[index - 1].focus();
            } else {
                const newCode = [...code];
                newCode[index] = "";
                setCode(newCode);
            }
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        const paste = e.clipboardData.getData("text").replace(/\D/g, "");
        if (!paste) return;

        const newCode = [...code];
        for (let i = 0; i < 6; i++) {
            newCode[i] = paste[i] || "";
        }
        setCode(newCode);

        const inputs = document.querySelectorAll(".verification-code-input");
        const lastFilledIndex = Math.min(paste.length, inputs.length) - 1;
        if (lastFilledIndex >= 0) {
            inputs[lastFilledIndex].focus();
        }

        if (paste.length >= 6) {
            handleVerify(paste.slice(0, 6));
        }
    };

    const showDangerText = async () => {
        const dangerSpan = document.querySelector(".text-danger");
        dangerSpan.textContent = 'Попробуйте еще раз';
    };

    const hiddenDangerText = async () => {
        const dangerSpan = document.querySelector(".text-danger");
        dangerSpan.textContent = '';
    };

    const handleVerify = async (fullCode) => {
        try {
            await verify(user_id, fullCode);
            navigate("/");
        } catch (err) {
            showDangerText();
        }
    };

    const handleClick = () => {
        const inputs = document.querySelectorAll(".verification-code-input");
        const firstEmpty = code.findIndex((c) => c === "");
        const focusIndex = firstEmpty === -1 ? 5 : firstEmpty;
        inputs[focusIndex].focus();
    };

    return (
        <>
            <div
                className="verification-code-container mt-4"
                onPaste={handlePaste}
                onClick={handleClick}>
                {code.map((num, index) => (
                    <input
                        key={index}
                        type="text"
                        inputMode="numeric"
                        maxLength="1"
                        className="verification-code-input"
                        value={num}
                        onChange={(e) =>
                            handleChange(e.target.value, index)
                        }
                        onKeyDown={(e) => handleBackspace(e, index)}
                        style={{
                            width: "44px",
                            height: "44px",
                            margin: "0 5px",
                            textAlign: "center",
                            fontSize: "1.3rem",
                            borderRadius: "10px",
                            border: "1px solid #ced4da",
                            outline: "none",
                            transition: "all 0.15s ease",
                        }}/>
                    ))}
                    <style>
                        {`
                            .verification-code-input:focus {
                                border-color: #0d6efd !important;
                                box-shadow: 0 0 8px rgba(13, 110, 253, 0.4) !important;
                                transform: scale(1.05);
                            }
                            .verification-code-input {
                                caret-color: transparent;
                            }
                        `}
                    </style>
                </div>
                <div className="d-flex justify-content-center mt-3">
                    <span className="text-danger"></span>
                </div>
        </>
    );
}

export default InputField;
