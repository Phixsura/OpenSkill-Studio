import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CostAllocatorCard from "../src/components/api-developer-platform-sdk-consumer-api-cost-allocator-card";

describe("CostAllocatorCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<CostAllocatorCard />);
    expect(container.textContent).toContain("Cost Allocator");
    expect(container.textContent).toContain("ep-users");
    expect(container.textContent).toContain("ep-search");
  });

  it("shows costs and total", () => {
    const { container } = render(<CostAllocatorCard />);
    expect(container.textContent).toContain("$57.00");
    expect(container.textContent).toContain("Total: $277.00");
  });
});
