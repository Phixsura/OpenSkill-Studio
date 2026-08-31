import { cn } from "@/lib/utils";
import { StatusBadgeClass } from "@/lib/cp";

export function StatusBadge({ status, className }: { status: string; className?: string }) {
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
