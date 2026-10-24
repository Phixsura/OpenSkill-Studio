import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FullErrorPage } from "@/components/full-error-page";

describe("FullErrorPage", () => {
  it("renders", () => {
    const { container } = render(
      <FullErrorPage statusCode={404} title="Not Found" icon="🔍"
        message="Page doesn't exist" suggestions={["Check URL", "Go home"]}
        onGoHome={vi.fn()} onGoBack={vi.fn()} />
    );
    expect(container.textContent).toContain("404");
    expect(container.textContent).toContain("Not Found");
    expect(container.textContent).toContain("🔍");
    expect(container.textContent).toContain("Check URL");
    expect(container.textContent).toContain("Home");
  });
  it("go home", () => {
    const fn = vi.fn();
    const { container } = render(
      <FullErrorPage statusCode={500} title="Error" icon="💥" message="Oops"
        suggestions={[]} onGoHome={fn} onGoBack={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Home")!);
    expect(fn).toHaveBeenCalled();
  });
});
