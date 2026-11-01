import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecurityOverviewCard } from "@/components/security-overview-card";

describe("SecurityOverviewCard", () => {
  it("secure", () => {
    const { container } = render(<SecurityOverviewCard score={95} grade="A" critical={0} high={0} needsAttention={false} />);
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("95/100");
  });
  it("vulnerable", () => {
    const { container } = render(<SecurityOverviewCard score={40} grade="F" critical={2} high={3} needsAttention={true} />);
    expect(container.textContent).toContain("F");
    expect(container.textContent).toContain("2 critical");
    expect(container.textContent).toContain("3 high");
  });
});
