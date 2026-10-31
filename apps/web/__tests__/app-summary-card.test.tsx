import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSummaryCard } from "@/components/app-summary-card";

describe("AppSummaryCard", () => {
  it("renders card", () => {
    const { container } = render(
      <AppSummaryCard name="SuperApp" icon="🚀" tagline="Do more" version="2.0.0"
        stars="★★★★☆" installsDisplay="25K" verified={true} category="tools"
        author="Alice" onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("★★★★☆");
    expect(container.textContent).toContain("25K");
    expect(container.textContent).toContain("by Alice");
    expect(container.textContent).toContain("✓");
  });
  it("clicks", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppSummaryCard name="X" icon="📦" tagline="" version="1.0" stars="" installsDisplay="0"
        verified={false} category="" author="" onClick={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
