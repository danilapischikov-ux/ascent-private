import { useState, type FormEvent } from "react";
import logo from "@/assets/logo.jpg";

const paymentLeadsEndpoint = import.meta.env.VITE_PAYMENT_LEADS_ENDPOINT?.trim();

const links = [
  { href: "#solve", label: "Что мы решаем" },
  { href: "#consulting", label: "Профессиональный консалтинг" },
  { href: "#process", label: "Как мы работаем" },
  { href: "#audience", label: "Кому подходим" },
  { href: "#why", label: "Почему Ascent Private" },
  { href: "#faq", label: "FAQ" },
];

export function Footer() {
  const [paymentData, setPaymentData] = useState({
    name: "",
    email: "",
    phone: "",
  });
  const [acceptedOffer, setAcceptedOffer] = useState(false);
  const [acceptedPolicy, setAcceptedPolicy] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [isPaymentSending, setIsPaymentSending] = useState(false);
  const hasPaymentData =
    Boolean(paymentData.name.trim()) &&
    Boolean(paymentData.email.trim()) &&
    Boolean(paymentData.phone.trim());
  const canPay = acceptedOffer && acceptedPolicy && hasPaymentData && !isPaymentSending;

  async function handlePaymentSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!paymentLeadsEndpoint) {
      return;
    }

    setIsPaymentSending(true);

    try {
      const payload = {
        name: paymentData.name.trim(),
        email: paymentData.email.trim(),
        phone: paymentData.phone.trim(),
        acceptedOffer,
        acceptedPolicy,
        source: window.location.href,
        submittedAt: new Date().toISOString(),
      };
      const body = JSON.stringify(payload);
      const sentByBeacon =
        "sendBeacon" in navigator &&
        navigator.sendBeacon(
          paymentLeadsEndpoint,
          new Blob([body], { type: "text/plain;charset=utf-8" }),
        );

      if (!sentByBeacon) {
        const response = await fetch(paymentLeadsEndpoint, {
          method: "POST",
          mode: "no-cors",
          keepalive: true,
          headers: {
            "Content-Type": "text/plain;charset=utf-8",
          },
          body,
        });

        if (response.type !== "opaque" && !response.ok) {
          throw new Error("Payment lead request failed");
        }
      }

      setPaymentData({ name: "", email: "", phone: "" });
      setAcceptedOffer(false);
      setAcceptedPolicy(false);
    } catch {
      // Keep the form filled so the user can try again.
    } finally {
      setIsPaymentSending(false);
    }
  }

  return (
    <footer className="border-t border-border bg-background px-4 sm:px-5 lg:px-10">
      <div className="mx-auto max-w-7xl py-10 sm:py-12 md:py-18">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
          <div className="lg:col-span-4">
            <img src={logo} alt="ASCENT PRIVATE" className="h-14 w-auto rounded-sm mb-6" />
            <p className="text-sm text-muted-foreground leading-relaxed max-w-md">
              Ascent Private — частный финансовый консалтинг для состоятельных инвесторов,
              сфокусированная на рынке США, опционных стратегиях, сценарном анализе и
              риск-интеллекте.
            </p>
          </div>

          <nav className="footer-nav lg:col-span-4">
            <p className="text-xs uppercase tracking-[0.26em] text-gold mb-5">Навигация</p>
            <ul className="grid grid-cols-1 gap-3">
              {links.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-gold transition whitespace-nowrap"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
              <li>
                <a
                  href="/cookies-policy"
                  className="text-sm text-muted-foreground hover:text-gold transition whitespace-nowrap"
                >
                  Политика Cookies
                </a>
              </li>
              <li>
                <a
                  href="/private-policy/"
                  className="text-sm text-muted-foreground hover:text-gold transition whitespace-nowrap"
                >
                  Политика обработки ПД
                </a>
              </li>
              <li>
                <a
                  href="https://cloud.mail.ru/public/g9Vz/uNb8J6sBZ"
                  className="text-sm text-muted-foreground hover:text-gold transition whitespace-nowrap"
                  target="_blank"
                  rel="noreferrer"
                >
                  Оферта
                </a>
              </li>
              <li>
                <a
                  href="https://cloud.mail.ru/public/rHMn/3P5qucwii"
                  className="text-sm text-muted-foreground hover:text-gold transition"
                  target="_blank"
                  rel="noreferrer"
                >
                  Согласие на получение информационной рассылки
                </a>
              </li>
            </ul>
          </nav>

          <form
            className="payment-form lg:col-span-4"
            onSubmit={handlePaymentSubmit}
            aria-label="Форма оплаты"
          >
            <div className="payment-fields">
              <input
                type="text"
                name="name"
                className="payment-input"
                placeholder={focusedField === "name" ? "" : "Имя"}
                value={paymentData.name}
                required
                autoComplete="name"
                onChange={(event) =>
                  setPaymentData((data) => ({ ...data, name: event.target.value }))
                }
                onFocus={() => setFocusedField("name")}
                onBlur={() => setFocusedField(null)}
              />
              <input
                type="email"
                name="email"
                className="payment-input"
                placeholder={focusedField === "email" ? "" : "Эл. почта (Email)"}
                value={paymentData.email}
                required
                autoComplete="email"
                onChange={(event) =>
                  setPaymentData((data) => ({ ...data, email: event.target.value }))
                }
                onFocus={() => setFocusedField("email")}
                onBlur={() => setFocusedField(null)}
              />
              <input
                type="tel"
                name="phone"
                className="payment-input"
                placeholder={focusedField === "phone" ? "" : "Номер телефона"}
                value={paymentData.phone}
                required
                autoComplete="tel"
                onChange={(event) =>
                  setPaymentData((data) => ({ ...data, phone: event.target.value }))
                }
                onFocus={() => setFocusedField("phone")}
                onBlur={() => setFocusedField(null)}
              />
            </div>

            <button
              type="submit"
              className="ascent-button payment-submit text-primary-foreground bg-gradient-gold shadow-gold"
              disabled={!canPay}
            >
              {isPaymentSending ? "Отправляем..." : "Оплатить"}
            </button>

            <div className="payment-checkboxes">
              <label className="payment-checkbox-row">
                <input
                  type="checkbox"
                  checked={acceptedOffer}
                  onChange={(event) => setAcceptedOffer(event.target.checked)}
                />
                <span>«Я принимаю условия Оферты»</span>
              </label>

              <label className="payment-checkbox-row">
                <input
                  type="checkbox"
                  checked={acceptedPolicy}
                  onChange={(event) => setAcceptedPolicy(event.target.checked)}
                />
                <span>
                  «Я даю Согласие на обработку моих персональных данных в соответствии с Политикой.
                  С Политикой обработки персональных данных ознакомлен(а) и согласен(а).»
                </span>
              </label>
            </div>
          </form>
        </div>

        <div className="mt-10 sm:mt-12 pt-7 sm:pt-8 border-t border-border">
          <p className="text-xs text-muted-foreground/82 leading-relaxed text-justify">
            Ascent Private не является зарегистрированным инвестиционным консультантом (RIA),
            брокером-дилером, финансовым аналитиком, брокерской компанией или инвестиционной фирмой.
            Информация на сайте носит исключительно информационно-аналитический характер и не
            является индивидуальной инвестиционной рекомендацией, публичной офертой, предложением по
            доверительному управлению, брокерской услугой или гарантией доходности. Инвестирование
            на финансовых рынках связано с риском, включая риск потери капитала. Пользователи
            самостоятельно принимают все инвестиционные решения и несут полную ответственность за
            возможные риски и последствия. Перед принятием инвестиционных решений необходимо
            самостоятельно оценить риски и при необходимости обратиться к лицензированным
            финансовым, юридическим и налоговым консультантам.
          </p>
        </div>
      </div>
    </footer>
  );
}
