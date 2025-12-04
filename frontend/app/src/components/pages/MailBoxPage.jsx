import React, {useEffect, useState, useContext} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods";
import Header from "../layouts/Header";
import api from "../../js/api";
import "bootstrap-icons/font/bootstrap-icons.css";

export default function MailBoxPage() {
  const [offers, setOffers] = useState([]);
  const [purchases, setPurchases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const [activeTab, setActiveTab] = useState("notifications"); // notifications, purchases, sales
  const [expandedProducts, setExpandedProducts] = useState({}); // {offerId: productData}
  const [loadingProducts, setLoadingProducts] = useState({}); // {offerId: true/false}
  const [buyerUsernames, setBuyerUsernames] = useState({}); // {buyerId: username}
  const {user, getProduct} = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOffers = async () => {
      try {
        const res = await api.get("/users/offers/");
        const offersData = res.data || [];

        // Загружаем username и tg_username для всех уникальных buyer_id
        const uniqueBuyerIds = [
          ...new Set(offersData.map((offer) => offer.buyer_id)),
        ];
        const userPromises = uniqueBuyerIds.map(async (buyerId) => {
          try {
            const userRes = await api.get(`/users/${buyerId}/`);
            return {
              buyerId,
              username: userRes.data.username,
              tg_username: userRes.data.tg_username,
            };
          } catch (err) {
            console.error(
              `Failed to fetch user info for buyer ${buyerId}:`,
              err
            );
            return {
              buyerId,
              username: `ID: ${buyerId}`,
              tg_username: null,
            };
          }
        });
        const userResults = await Promise.all(userPromises);
        const usernameMap = {};
        const offersWithTg = offersData.map((offer) => {
          const buyerInfo = userResults.find(
            (info) => info.buyerId === offer.buyer_id
          );
          return {
            ...offer,
            tg_username: buyerInfo?.tg_username || null,
          };
        });

        userResults.forEach(({buyerId, username}) => {
          usernameMap[buyerId] = username;
        });
        setBuyerUsernames(usernameMap);
        setOffers(offersWithTg);
      } catch (err) {
        console.error("Failed to fetch offers:", err);
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchOffers();
    }
  }, [user]);

  useEffect(() => {
    const fetchPurchases = async () => {
      if (activeTab === "purchases" && user) {
        try {
          const res = await api.get("/users/purchases/");
          const purchasesData = res.data || [];

          // Загружаем username и tg_username для всех уникальных seller_id из покупок
          const uniqueSellerIds = [
            ...new Set(purchasesData.map((purchase) => purchase.seller_id)),
          ];
          const userPromises = uniqueSellerIds.map(async (sellerId) => {
            try {
              const userRes = await api.get(`/users/${sellerId}/`);
              return {
                sellerId,
                username: userRes.data.username,
                tg_username: userRes.data.tg_username,
              };
            } catch (err) {
              console.error(
                `Failed to fetch user info for seller ${sellerId}:`,
                err
              );
              return {
                sellerId,
                username: `ID: ${sellerId}`,
                tg_username: null,
              };
            }
          });
          const userResults = await Promise.all(userPromises);
          const usernameMap = {...buyerUsernames};
          const purchasesWithTg = purchasesData.map((purchase) => {
            const sellerInfo = userResults.find(
              (info) => info.sellerId === purchase.seller_id
            );
            return {
              ...purchase,
              tg_username: sellerInfo?.tg_username || null,
            };
          });

          userResults.forEach(({sellerId, username}) => {
            usernameMap[sellerId] = username;
          });
          setBuyerUsernames(usernameMap);
          setPurchases(purchasesWithTg);
        } catch (err) {
          console.error("Failed to fetch purchases:", err);
        }
      }
    };

    fetchPurchases();
  }, [activeTab, user]);

  const handleAccept = async (offerId) => {
    try {
      await api.patch(`/purchases/accept/${offerId}`);
      // Обновляем состояние предложения
      setOffers((prevOffers) =>
        prevOffers.map((offer) =>
          offer.id === offerId
            ? {...offer, permission: true, successful: true}
            : offer
        )
      );
    } catch (err) {
      console.error("Failed to accept offer:", err);
    }
  };

  const handleReject = async (offerId) => {
    try {
      await api.patch(`/purchases/reject/${offerId}`);
      // Обновляем состояние предложения
      setOffers((prevOffers) =>
        prevOffers.map((offer) =>
          offer.id === offerId
            ? {...offer, refusal: true, successful: false}
            : offer
        )
      );
    } catch (err) {
      console.error("Failed to reject offer:", err);
    }
  };

  // Фильтруем предложения по активной вкладке
  const filteredOffers = (() => {
    if (activeTab === "notifications") {
      // Уведомления: не показываем предложения
      return [];
    } else if (activeTab === "purchases") {
      // Покупки: используем данные из отдельного запроса
      return purchases;
    } else if (activeTab === "sales") {
      // Продажи: предложения, где пользователь является продавцом
      return offers.filter((offer) => offer.seller_id === user?.id);
    }
    return [];
  })();

  // Сортируем предложения: новые -> принятые -> отклоненные
  const sortedOffers = [...filteredOffers].sort((a, b) => {
    // Новые предложения (без permission и refusal) - вверху
    const aIsNew = !a.permission && !a.refusal;
    const bIsNew = !b.permission && !b.refusal;
    if (aIsNew && !bIsNew) return -1;
    if (!aIsNew && bIsNew) return 1;

    // Принятые (permission = true) - после новых
    if (a.permission && !b.permission) return -1;
    if (!a.permission && b.permission) return 1;

    // Отклоненные (refusal = true) - внизу
    if (a.refusal && !b.refusal) return 1;
    if (!a.refusal && b.refusal) return -1;

    // Если статус одинаковый, сортируем по дате (новые выше)
    return new Date(b.created_at) - new Date(a.created_at);
  });

  // Подсчитываем новые предложения для текущей вкладки
  const newOffersCount = filteredOffers.filter(
    (offer) => !offer.permission && !offer.refusal
  ).length;

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString("ru-RU", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  const handleViewProduct = async (offerId, productId) => {
    // Если товар уже загружен, просто переключаем видимость
    if (expandedProducts[offerId]) {
      setExpandedProducts((prev) => {
        const newState = {...prev};
        delete newState[offerId];
        return newState;
      });
      return;
    }

    // Загружаем информацию о товаре
    setLoadingProducts((prev) => ({...prev, [offerId]: true}));
    try {
      const productData = await getProduct(productId);
      setExpandedProducts((prev) => ({...prev, [offerId]: productData}));
    } catch (err) {
      console.error("Failed to load product:", err);
    } finally {
      setLoadingProducts((prev) => ({...prev, [offerId]: false}));
    }
  };

  if (isLoading)
    return (
      <div>
        <Header />
        <div className="spinner" />
      </div>
    );

  return (
    <div>
      <Header />
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
          padding: "var(--spacing-md)",
          minHeight: "calc(100vh - 100px)",
        }}
      >
        <div
          style={{
            position: "fixed",
            top: "100px",
            left: "50%",
            transform: "translateX(-50%)",
            width: "min(800px, calc(100vw - 2 * var(--spacing-md)))",
            maxWidth: "800px",
            height: "calc(100vh - 100px)",
            backgroundColor: "#fff",
            borderRadius: "14px",
            border: "2px solid var(--color-border-light)",
            padding: "var(--spacing-md)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-around",
              gap: "var(--spacing-sm)",
              marginBottom: "var(--spacing-md)",
              overflowX: "auto",
              overflowY: "hidden",
              flexWrap: "nowrap",
              paddingTop: "25px",
              paddingBottom: "25px",
            }}
          >
            <button
              className={`button-reverse ${
                activeTab === "notifications" ? "active" : ""
              }`}
              onClick={() => setActiveTab("notifications")}
              style={{
                backgroundColor:
                  activeTab === "notifications"
                    ? "var(--color-primary)"
                    : "transparent",
                color:
                  activeTab === "notifications"
                    ? "var(--color-text-light)"
                    : "var(--color-primary)",
              }}
            >
              Уведомления
            </button>
            <button
              className={`button-reverse ${
                activeTab === "purchases" ? "active" : ""
              }`}
              onClick={() => setActiveTab("purchases")}
              style={{
                backgroundColor:
                  activeTab === "purchases"
                    ? "var(--color-primary)"
                    : "transparent",
                color:
                  activeTab === "purchases"
                    ? "var(--color-text-light)"
                    : "var(--color-primary)",
              }}
            >
              Покупки
            </button>
            <button
              className={`button-reverse ${
                activeTab === "sales" ? "active" : ""
              }`}
              onClick={() => setActiveTab("sales")}
              style={{
                backgroundColor:
                  activeTab === "sales"
                    ? "var(--color-primary)"
                    : "transparent",
                color:
                  activeTab === "sales"
                    ? "var(--color-text-light)"
                    : "var(--color-primary)",
              }}
            >
              Продажи
            </button>
          </div>

          <div
            style={{
              flex: 1,
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: "var(--spacing-sm)",
            }}
          >
            {sortedOffers.length === 0 ? (
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  height: "100%",
                  color: "var(--color-text-muted)",
                }}
              >
                Нет предложений
              </div>
            ) : (
              sortedOffers.map((offer) => {
                const isAccepted = offer.permission === true;
                const isRejected = offer.refusal === true;
                const isExpanded = !!expandedProducts[offer.id];
                const isLoadingProduct = loadingProducts[offer.id];

                return (
                  <div
                    key={offer.id}
                    className={`offer-card ${
                      isAccepted ? "accepted" : isRejected ? "rejected" : ""
                    } ${isExpanded && expandedProducts[offer.id] ? "expanded" : ""}`}
                  >
                    <div
                      className="offer-card-content"
                      onClick={() =>
                        handleViewProduct(offer.id, offer.product_id)
                      }
                      style={{cursor: "pointer"}}
                    >
                      <div className="offer-user-info">
                        <div className="offer-user-header">
                          <img
                            src="/blue-avatar.png"
                            alt="Avatar"
                            className="offer-avatar"
                          />
                          <span className="offer-username">
                            {activeTab === "purchases"
                              ? buyerUsernames[offer.seller_id] ||
                                `ID: ${offer.seller_id}`
                              : buyerUsernames[offer.buyer_id] ||
                                `ID: ${offer.buyer_id}`}
                          </span>
                        </div>
                        <div className="offer-comment">
                          {offer.comment || "Без комментария"}
                        </div>
                        <div className="offer-date">
                          {formatDate(offer.created_at)}
                        </div>
                      </div>
                      {activeTab === "purchases" ? (
                        <div className="offer-actions">
                          {isRejected && (
                            <span style={{color: "var(--color-danger)"}}>
                              Отказано
                            </span>
                          )}
                          {isAccepted && offer.tg_username && (
                            <div
                              style={{
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "flex-end",
                                gap: "4px",
                              }}
                            >
                              <span>Связаться с продавцом</span>
                              <a
                                href={`https://t.me/${offer.tg_username}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                style={{
                                  color: "var(--color-primary)",
                                  textDecoration: "underline",
                                }}
                              >
                                @{offer.tg_username}
                              </a>
                            </div>
                          )}
                          {!isAccepted && !isRejected && (
                            <span>В ожидании ответа</span>
                          )}
                        </div>
                      ) : activeTab === "sales" ? (
                        <div className="offer-actions">
                          {isRejected && (
                            <span style={{color: "var(--color-danger)"}}>
                              Отказано
                            </span>
                          )}
                          {isAccepted && offer.tg_username && (
                            <div
                              style={{
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "flex-end",
                                gap: "4px",
                              }}
                            >
                              <span>Связаться с покупателем</span>
                              <a
                                href={`https://t.me/${offer.tg_username}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                style={{
                                  color: "var(--color-primary)",
                                  textDecoration: "underline",
                                }}
                              >
                                @{offer.tg_username}
                              </a>
                            </div>
                          )}
                          {!isAccepted && !isRejected && (
                            <div
                              className="offer-actions"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <button
                                className="offer-action-btn accept"
                                onClick={() => handleAccept(offer.id)}
                                title="Принять"
                              >
                                <i
                                  className="bi bi-check-lg"
                                  style={{fontSize: "20px"}}
                                />
                              </button>
                              <button
                                className="offer-action-btn reject"
                                onClick={() => handleReject(offer.id)}
                                title="Отклонить"
                              >
                                <i
                                  className="bi bi-x-lg"
                                  style={{fontSize: "20px"}}
                                />
                              </button>
                            </div>
                          )}
                        </div>
                      ) : (
                        !isAccepted &&
                        !isRejected && (
                          <div
                            className="offer-actions"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <button
                              className="offer-action-btn accept"
                              onClick={() => handleAccept(offer.id)}
                              title="Принять"
                            >
                              <i
                                className="bi bi-check-lg"
                                style={{fontSize: "20px"}}
                              />
                            </button>
                            <button
                              className="offer-action-btn reject"
                              onClick={() => handleReject(offer.id)}
                              title="Отклонить"
                            >
                              <i
                                className="bi bi-x-lg"
                                style={{fontSize: "20px"}}
                              />
                            </button>
                          </div>
                        )
                      )}
                    </div>
                    <div className="offer-product-card">
                      {isLoadingProduct ? (
                        <div>Загрузка...</div>
                      ) : expandedProducts[offer.id] ? (
                        <div className="offer-product-content">
                          {expandedProducts[offer.id].images &&
                          expandedProducts[offer.id].images.length > 0 ? (
                            <img
                              src={
                                expandedProducts[offer.id].images.find(
                                  (img) => img.is_main
                                )?.url ||
                                expandedProducts[offer.id].images[0]?.url
                              }
                              alt={expandedProducts[offer.id].name}
                              className="offer-product-image"
                            />
                          ) : (
                            <div
                              className="offer-product-image"
                              style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                backgroundColor: "var(--color-bg)",
                              }}
                            >
                              Нет изображения
                            </div>
                          )}
                          <div className="offer-product-info">
                            <div className="offer-product-name">
                              {expandedProducts[offer.id].name}
                            </div>
                            <div className="offer-product-description">
                              {truncateText(
                                expandedProducts[offer.id].description,
                                100
                              )}
                            </div>
                            <div className="offer-product-price">
                              {expandedProducts[offer.id].price} ₽
                            </div>
                          </div>
                        </div>
                      ) : null}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
