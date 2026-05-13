import Image from "next/image";

/** Local asset from `Screens/hero image.png` (served as `/hero-image.png`). */
const HERO_SRC = "/hero-image.png";

export function FoodHero() {
  return (
    <section
      className="relative isolate h-[220px] w-full overflow-hidden sm:h-[280px] md:h-[340px] lg:h-[400px]"
      aria-label="Hero"
    >
      <Image
        src={HERO_SRC}
        alt="Gourmet appetizer platter with tapas-style dishes in a warm restaurant setting"
        fill
        priority
        className="object-cover object-center"
        sizes="100vw"
      />
      <div
        className="pointer-events-none absolute inset-0 bg-gradient-to-t from-zomato-dark via-zomato-dark/55 to-zomato-dark/10"
        aria-hidden
      />
      <div className="absolute inset-x-0 bottom-0 z-10 mx-auto max-w-6xl px-4 pb-6 pt-16 sm:px-6 sm:pb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-green">Fresh picks</p>
        <h2 className="mt-1 max-w-xl text-2xl font-bold leading-tight tracking-tight text-white drop-shadow-md sm:text-3xl md:text-4xl">
          Flavor worth leaving home for.
        </h2>
        <p className="mt-2 max-w-md text-sm text-zinc-200/90 drop-shadow sm:text-base">
          Scroll down and tell us what you&apos;re in the mood for — we&apos;ll match you to spots you&apos;ll love.
        </p>
      </div>
    </section>
  );
}
