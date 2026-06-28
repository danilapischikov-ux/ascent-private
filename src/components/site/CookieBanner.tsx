import { useEffect, useState } from "react";

const COOKIE_CONSENT_KEY = "ascent_cookie_consent_yandex_metrika";

export function CookieBanner() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(localStorage.getItem(COOKIE_CONSENT_KEY) !== "accepted");
  }, []);

  const acceptCookies = () => {
    localStorage.setItem(COOKIE_CONSENT_KEY, "accepted");
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="cookie-banner" role="dialog" aria-live="polite" aria-label="Cookie">
      <div className="cookie-banner-inner">
        <p className="cookie-banner-text">
          На сайте используются файлы Cookie Яндекс Метрики для анализа трафика, действий и
          предпочтений посетителей сайта. Подробнее в{" "}
          <a href="/cookies-policy" className="cookie-banner-link">
            Политика использования файлов Cookies
          </a>
          . Нажимая «Принять» или оставаясь на сайте, вы даете согласие на это.
        </p>
        <button type="button" className="cookie-banner-button" onClick={acceptCookies}>
          Принять
        </button>
      </div>
    </div>
  );
}
