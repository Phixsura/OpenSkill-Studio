import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RateLimitPolicyCard from "../src/components/api-developer-platform-sdk-consumer-api-rate-limit-policy-card";

describe("RateLimitPolicyCard", () => {
  it("renders title and policies", () => {
    const { container } = render(<RateLimitPolicyCard />);
    expect(container.textContent).toContain("Rate Limit Policy");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/search");
  });

  it("shows deny rate", () => {
    const { container } = render(<RateLimitPolicyCard />);
    expect(container.textContent).toContain("3.4% deny rate");
    expect(container.textContent).toContain("+20 burst");
  });
});
