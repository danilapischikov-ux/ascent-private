import logo from "@/assets/logo.jpg";

const links = [
  { href: "#solve", label: "Что мы решаем" },
  { href: "#consulting", label: "Профессиональный консалтинг" },
  { href: "#process", label: "Как мы работаем" },
  { href: "#audience", label: "Кому подходим" },
  { href: "#why", label: "Почему Ascent Private" },
  { href: "#faq", label: "FAQ" },
];

export function Footer() {
  return (
    <footer className="border-t border-border bg-background px-4 sm:px-5 lg:px-10">
      <div className="mx-auto max-w-7xl py-10 sm:py-12 md:py-18">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
          <div className="lg:col-span-5">
            <img src={logo} alt="ASCENT PRIVATE" className="h-14 w-auto rounded-sm mb-6" />
            <p className="text-sm text-muted-foreground leading-relaxed max-w-md">
              Ascent Private — частный финансовый консалтинг для состоятельных инвесторов,
              сфокусированная на рынке США, опционных стратегиях, сценарном анализе и
              риск-интеллекте.
            </p>
          </div>

          <nav className="lg:col-span-4">
            <p className="text-xs uppercase tracking-[0.26em] text-gold mb-5">Навигация</p>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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
            </ul>
          </nav>
        </div>

        <div className="mt-10 sm:mt-12 pt-7 sm:pt-8 border-t border-border">
          <p className="text-xs text-muted-foreground/82 leading-relaxed">
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
