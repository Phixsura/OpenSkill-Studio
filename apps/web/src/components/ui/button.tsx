import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "outline" | "destructive";
  size?: "default" | "sm";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "default", ...props }, ref) => {
    const variants = {
      primary:
        "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90",
      secondary:
        "border bg-[hsl(var(--secondary))] text-[hsl(var(--secondary-foreground))] hover:opacity-90",
      ghost: "hover:bg-[hsl(var(--secondary))]",
      outline: "border hover:bg-[hsl(var(--secondary))]",
      destructive:
        "bg-[hsl(var(--destructive))] text-white hover:opacity-90",
    };

    const sizes = {
      default: "px-4 py-2",
      sm: "px-3 py-1.5 text-xs",
    };

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium",
          "disabled:pointer-events-none disabled:opacity-50",
          "transition-opacity",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2",
          variants[variant],
          sizes[size],
          className,
        )}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";
