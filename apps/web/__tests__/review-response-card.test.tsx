import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewResponseCard } from "@/components/review-response-card";

describe("ReviewResponseCard", () => {
  it("renders with response", () => {
    const { container } = render(
      <ReviewResponseCard rating={4} title="Good app" body="Works well" author="Alice"
        responseBody="Thank you!" respondedAt="2026-01-02" onRespond={vi.fn()} />
    );
    expect(container.textContent).toContain("Good app");
    expect(container.textContent).toContain("★★★★☆");
    expect(container.textContent).toContain("Developer Response");
    expect(container.textContent).toContain("Thank you!");
  });
  it("renders without response", () => {
    const { container } = render(
      <ReviewResponseCard rating={3} title="OK" body="Average" author="Bob"
        responseBody={null} respondedAt={null} onRespond={vi.fn()} />
    );
    expect(container.textContent).toContain("Reply to review");
  });
});
