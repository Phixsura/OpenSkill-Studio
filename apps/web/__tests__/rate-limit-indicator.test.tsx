import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitIndicator } from "@/components/rate-limit-indicator";

describe("RateLimitIndicator", () => {
  it("shows remaining", () => {
    const { container } = render(<RateLimitIndicator remaining={50} limit={100} resetIn={30} />);
    expect(container.textContent).toContain("50/100");
  });
  it("shows reset time", () => {
    const { container } = render(<RateLimitIndicator remaining={10} limit={100} resetIn={45} />);
    expect(container.textContent).toContain("45s");
  });
});
