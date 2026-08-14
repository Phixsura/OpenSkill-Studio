import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-lg text-[hsl(var(--muted-foreground))]">
        Page not found
      </p>
      <Link
        href="/"
        className="rounded-md bg-[hsl(var(--primary))] px-5 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
      >
        Go to home
      </Link>
    </main>
  );
}
