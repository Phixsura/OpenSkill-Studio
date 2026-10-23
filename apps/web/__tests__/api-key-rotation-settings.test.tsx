import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyRotationSettings } from "@/components/api-key-rotation-settings";

describe("ApiKeyRotationSettings", () => {
  it("renders", () => {
    const { container } = render(
      <ApiKeyRotationSettings maxAgeDays={90} overlapHours={24} autoRotate={true}
        nextRotationDays={45} policySummary="Auto every 90 days"
        onRotateNow={vi.fn()} onToggleAuto={vi.fn()} />
    );
    expect(container.textContent).toContain("Key Rotation Policy");
    expect(container.textContent).toContain("90d");
    expect(container.textContent).toContain("24h");
    expect(container.textContent).toContain("45d");
    expect(container.textContent).toContain("Auto every 90 days");
  });
  it("rotate now", () => {
    const fn = vi.fn();
    const { container } = render(
      <ApiKeyRotationSettings maxAgeDays={90} overlapHours={24} autoRotate={true}
        nextRotationDays={45} policySummary="x" onRotateNow={fn} onToggleAuto={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Rotate Now")!);
    expect(fn).toHaveBeenCalled();
  });
});
