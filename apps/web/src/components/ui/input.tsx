import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export type InputProps = InputHTMLAttributes<HTMLInputElement>;

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none",
          "focus:ring-2 focus:ring-[hsl(var(--ring))]",
          "placeholder:text-[hsl(var(--muted-foreground))]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className,
        )}
        {...props}
      />
    );
  },
);
Input.displayName = "Input";
