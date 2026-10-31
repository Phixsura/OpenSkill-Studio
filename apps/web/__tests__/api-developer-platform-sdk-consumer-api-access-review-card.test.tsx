import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AccessReviewCard from "../src/components/api-developer-platform-sdk-consumer-api-access-review-card";

describe("AccessReviewCard", () => {
  it("renders title and reviews", () => {
    const { container } = render(<AccessReviewCard />);
    expect(container.textContent).toContain("Access Review");
    expect(container.textContent).toContain("2024-Q4");
    expect(container.textContent).toContain("2025-Q1");
  });

  it("shows progress", () => {
    const { container } = render(<AccessReviewCard />);
    expect(container.textContent).toContain("45/45 reviewed");
    expect(container.textContent).toContain("12/38 reviewed");
  });
});
