import React from "react";
import { useLocation } from "react-router-dom";
import InputField from "../buttons/InputField.jsx";
import SimpleHeader from "../layouts/SimpleHeader.jsx";

function VerifyPage() {
    const location = useLocation();
    const data = location.state?.data || {};
    const link = data.tg_url || "";
    return (
        <>
            <SimpleHeader />
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
                <InputField />
            </div>
        </>
    );
}

export default VerifyPage;
