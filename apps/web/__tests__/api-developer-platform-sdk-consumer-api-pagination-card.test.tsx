import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PaginationCard from "../src/components/api-developer-platform-sdk-consumer-api-pagination-card";

describe("PaginationCard", () => {
  it("renders title and config", () => {
    const { container } = render(<PaginationCard />);
    expect(container.textContent).toContain("Pagination Helper");
    expect(container.textContent).toContain("cursor");
    expect(container.textContent).toContain("20");
  });

  it("shows example metadata", () => {
    const { container } = render(<PaginationCard />);
    expect(container.textContent).toContain("has_more: true");
    expect(container.textContent).toContain("1,250 total");
  });
});
