import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--secondary))]">
      <div className="w-full max-w-md space-y-6 rounded-lg border bg-[hsl(var(--card))] p-8 shadow-sm">
        <div className="text-center">
          <Link href="/" className="text-xl font-bold tracking-tight">
            OpenSkill Studio
          </Link>
        </div>
        {children}
      </div>
    </div>
  );
}
