import { cn } from "@/lib/utils";
import { StatusBadgeClass } from "@/lib/cp";

export function StatusBadge({ status, className }: { status?: string | null; className?: string }) {
  // A missing status must never unmount the whole page tree (React render crash)
  if (!status) return null;
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        StatusBadgeClass(status),
        className,
      )}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}
