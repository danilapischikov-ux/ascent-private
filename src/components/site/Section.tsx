import type { ReactNode } from "react";

export function Section({
  id,
  eyebrow,
  title,
  subtitle,
  children,
  className = "",
  image,
  imagePosition = "center",
}: {
  id?: string;
  eyebrow?: string;
  title: ReactNode;
  subtitle?: ReactNode;
  children?: ReactNode;
  className?: string;
  image?: string;
  imagePosition?: string;
}) {
  return (
    <section
      id={id}
      className={`section-shell scroll-mt-24 md:scroll-mt-28 bg-background py-5 md:py-7 lg:py-8 px-4 sm:px-5 lg:px-10 ${className}`}
    >
      {image && (
        <div className="absolute inset-0 z-0" aria-hidden="true">
          <div
            className="section-media absolute inset-0 bg-cover opacity-34 md:opacity-42"
            style={{
              backgroundImage: `url(${image})`,
              backgroundPosition: imagePosition,
            }}
          />
          <div className="absolute inset-0 fine-grid opacity-55" />
          <div className="absolute inset-0 section-overlay" />
          <div className="absolute inset-0 section-glow" />
        </div>
      )}
      <div className="relative z-10 mx-auto max-w-7xl">
        <div className="max-w-3xl mb-8 sm:mb-10 md:mb-16 reveal">
          {eyebrow && (
            <div className="flex items-center gap-3 mb-4 sm:mb-6">
              <div className="h-px w-10 bg-gold/60" />
              <span className="text-xs uppercase tracking-[0.26em] text-gold">{eyebrow}</span>
            </div>
          )}
          <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl leading-[1.06] md:leading-[1.02] text-foreground">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-5 sm:mt-6 text-base md:text-lg text-muted-foreground leading-relaxed max-w-3xl">
              {subtitle}
            </p>
          )}
        </div>
        {children}
      </div>
    </section>
  );
}
