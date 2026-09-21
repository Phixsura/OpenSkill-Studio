import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "OpenSkill Studio",
  description:
    "AI-powered project-based training and delivery platform for creators",
};

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6">
      <h1 className="text-4xl font-bold tracking-tight">OpenSkill Studio</h1>
      <p className="text-lg text-[hsl(var(--muted-foreground))]">
        Project-based training and delivery platform for AI creators.
      </p>
      <div className="flex gap-3">
        <Link
          href="/login"
          className="rounded-md border px-5 py-2 text-sm font-medium hover:bg-[hsl(var(--secondary))]"
        >
          Log in
        </Link>
        <Link
          href="/register"
          className="rounded-md bg-[hsl(var(--primary))] px-5 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
        >
          Sign up
        </Link>
      </div>
    </main>
  );
}
