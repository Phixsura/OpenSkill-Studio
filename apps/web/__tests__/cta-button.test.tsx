import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CtaButton } from "@/components/cta-button";

describe("CtaButton", () => {
  it("renders", () => {
    const { container } = render(
      <CtaButton label="Get Started" classes="bg-blue-600 text-white" icon="🚀" onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("🚀");
    expect(container.textContent).toContain("Get Started");
  });
  it("click", () => {
    const fn = vi.fn();
    const { container } = render(
      <CtaButton label="Go" classes="" icon={null} onClick={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
  it("disabled", () => {
    const fn = vi.fn();
    const { container } = render(
      <CtaButton label="X" classes="" icon={null} onClick={fn} disabled />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).not.toHaveBeenCalled();
  });
});
