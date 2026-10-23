import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorResponseDisplay } from "@/components/error-response-display";

describe("ErrorResponseDisplay", () => {
  it("renders", () => {
    const error = { code: "NOT_FOUND", message: "App not found", status: 404 };
    const { container } = render(<ErrorResponseDisplay error={error} />);
    expect(container.textContent).toContain("404");
    expect(container.textContent).toContain("NOT_FOUND");
    expect(container.textContent).toContain("App not found");
    expect(container.textContent).toContain("🔍");
  });
  it("retry", () => {
    const fn = vi.fn();
    const error = { code: "INTERNAL_ERROR", message: "Oops", status: 500 };
    const { container } = render(<ErrorResponseDisplay error={error} onRetry={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Retry")!);
    expect(fn).toHaveBeenCalled();
  });
});
