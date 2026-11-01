import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RateLimitOverrideCard from "../src/components/rate-limit-override-card";

const overrides = [
  {
    override_id: "o1",
    consumer_id: "vip-app",
    limit: 1000,
    reason: "VIP customer",
    is_active: true,
    request_count: 450,
  },
  {
    override_id: "o2",
    consumer_id: "legacy-app",
    limit: 500,
    reason: "Migration",
    is_active: false,
    request_count: 200,
  },
];

describe("RateLimitOverrideCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<RateLimitOverrideCard overrides={overrides} appName="App" />);
    expect(container.textContent).toContain("Rate Overrides");
    expect(container.textContent).toContain("1/2 active");
  });

  it("shows consumer and limit", () => {
    const { container } = render(<RateLimitOverrideCard overrides={overrides} appName="App" />);
    expect(container.textContent).toContain("vip-app");
    expect(container.textContent).toContain("1000/min");
  });

  it("shows reason and usage", () => {
    const { container } = render(<RateLimitOverrideCard overrides={overrides} appName="App" />);
    expect(container.textContent).toContain("VIP customer");
    expect(container.textContent).toContain("450 used");
  });

  it("shows empty state", () => {
    const { container } = render(<RateLimitOverrideCard overrides={[]} appName="App" />);
    expect(container.textContent).toContain("No rate limit overrides");
  });
});
