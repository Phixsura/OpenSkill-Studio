import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CountBadge } from "@/components/count-badge";

describe("CountBadge", () => {
  it("renders count", () => {
    const { container } = render(
      <CountBadge count={5} display="5" visible={true} size="sm" urgency="medium" />
    );
    expect(container.textContent).toContain("5");
  });
  it("renders 99+", () => {
    const { container } = render(
      <CountBadge count={150} display="99+" visible={true} size="lg" urgency="high" />
    );
    expect(container.textContent).toContain("99+");
  });
  it("hidden when zero", () => {
    const { container } = render(
      <CountBadge count={0} display="0" visible={false} size="sm" urgency="low" />
    );
    expect(container.innerHTML).toBe("");
  });
});
