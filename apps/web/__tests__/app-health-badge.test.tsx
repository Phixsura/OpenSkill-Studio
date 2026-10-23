import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppHealthBadge } from "@/components/app-health-badge";

describe("AppHealthBadge", () => {
  it("renders badge", () => {
    const { container } = render(
      <AppHealthBadge score={100} grade="A" checks={[
        { metric: "Error Rate", value: "0.1%", score: 25, max: 25 },
        { metric: "Latency", value: "85ms", score: 25, max: 25 },
      ]} />
    );
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("Error Rate: 0.1%");
    expect(container.textContent).toContain("25/25");
  });
});
