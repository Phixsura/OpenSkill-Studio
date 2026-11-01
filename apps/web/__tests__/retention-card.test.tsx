import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RetentionCard } from "@/components/retention-card";

describe("RetentionCard", () => {
  it("shows rate", () => {
    const { container } = render(<RetentionCard totalInstalls={100} retained={80} churned={20} retentionRate={80} />);
    expect(container.textContent).toContain("80%");
  });
  it("shows counts", () => {
    const { container } = render(<RetentionCard totalInstalls={50} retained={45} churned={5} retentionRate={90} />);
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("5");
  });
});
