import React, { useContext, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import HomeButton from "../buttons/HomeButton.jsx";
import { AuthContext } from "../methods/ApiMethods.jsx";

function VerifyPage() {
    const { verify } = useContext(AuthContext);
    const location = useLocation();
    const data = location.state?.data || {};
    const user_id = data.user_id;
    const link = data.tg_url || "";
    const navigate = useNavigate();

    const [code, setCode] = useState(["", "", "", "", "", ""]);

    const handleChange = (value, index) => {
        if (!/^\d?$/.test(value)) return; // только цифры

        const newCode = [...code];
        newCode[index] = value;
        setCode(newCode);

        const inputs = document.querySelectorAll(".verification-code-input");

        if (value && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }

        // если все поля заполнены — отправляем
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

        // переносим фокус
        const inputs = document.querySelectorAll(".verification-code-input");
        const lastFilledIndex = Math.min(paste.length, inputs.length) - 1;
        if (lastFilledIndex >= 0) {
            inputs[lastFilledIndex].focus();
        }

        // если вставлено 6 символов — отправляем
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
            <HomeButton className="position-absolute top-0 start-0 m-3" />
            <div className="text-center m-4">
                <h1 className="fs-1">Подтверждение</h1>
            </div>

            <div className="d-flex flex-column justify-content-center align-items-center">
                <div className="d-flex flex-column qr-code">
                    <span className="text fs-5">
                        Пожалуйста, отсканируйте QR-код для подтверждения.
                    </span>
                    <img
                        src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
                            link
                        )}`}
                        alt="QR Code"
                        className="img-fluid rounded-3 d-block mx-auto m-3"
                    />
                </div>

                <div>
                    <span className="text fs-5">
                        Или перейдите по{" "}
                        <a href={link} className="text-decoration-none">
                            ссылке
                        </a>
                    </span>
                </div>

                <div
                    className="verification-code-container mt-4"
                    onPaste={handlePaste}
                    onClick={handleClick}
                >
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
                            }}
                        />
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
            </div>
        </>
    );
}

export default VerifyPage;
