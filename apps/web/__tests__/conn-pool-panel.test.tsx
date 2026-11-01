import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConnPoolPanel } from "@/components/conn-pool-panel";

const mockPools = [
  { target: "postgres", active: 5, idle: 3, total: 8, max: 10 },
  { target: "redis", active: 2, idle: 8, total: 10, max: 20 },
];

describe("ConnPoolPanel", () => {
  it("renders pools", () => {
    const { container } = render(<ConnPoolPanel pools={mockPools} />);
    expect(container.textContent).toContain("postgres");
    expect(container.textContent).toContain("5 active");
    expect(container.textContent).toContain("8/10 total");
    expect(container.textContent).toContain("80%");
  });
});
