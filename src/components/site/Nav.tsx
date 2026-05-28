import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import logo from "@/assets/logo.jpg";

const links = [
  { href: "/#solve", label: "Что мы решаем" },
  { href: "/#consulting", label: "Профессиональный консалтинг" },
  { href: "/#process", label: "Как мы работаем" },
  { href: "/#audience", label: "Кому подходим" },
  { href: "/#why", label: "Почему Ascent Private" },
  { href: "/#faq", label: "FAQ" },
];

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 18);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-500 ${
        scrolled || open
          ? "backdrop-blur-xl bg-background/88 border-b border-border"
          : "bg-gradient-to-b from-background/70 to-transparent"
      }`}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-5 lg:px-10 min-h-16 sm:min-h-20 flex items-center gap-5 py-2 sm:py-3">
        <a href="/#top" className="flex items-center gap-3 shrink-0" onClick={() => setOpen(false)}>
          <img src={logo} alt="Ascent Private" className="h-10 sm:h-11 w-auto rounded-sm" />
        </a>

        <nav className="hidden xl:flex absolute left-1/2 -translate-x-1/2 items-center justify-center gap-5">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-[13px] font-light tracking-[0.02em] text-foreground/78 hover:text-gold transition-colors whitespace-nowrap"
            >
              {l.label}
            </a>
          ))}
        </nav>

        <button
          type="button"
          aria-label="Меню"
          onClick={() => setOpen((value) => !value)}
          className="xl:hidden ml-auto size-10 sm:size-11 inline-flex items-center justify-center border border-border text-foreground hover:border-gold-soft hover:text-gold transition"
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      {open && (
        <div className="xl:hidden border-t border-border bg-background/96 backdrop-blur-xl">
          <nav className="mx-auto max-w-7xl px-4 sm:px-5 py-4 sm:py-5 grid gap-1">
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                className="py-3 text-base font-light text-foreground/88 hover:text-gold border-b border-border/45 transition-colors"
              >
                {l.label}
              </a>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
