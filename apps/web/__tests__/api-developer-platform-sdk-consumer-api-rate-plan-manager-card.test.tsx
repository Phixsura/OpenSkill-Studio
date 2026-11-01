import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RatePlanManagerCard from "../src/components/api-developer-platform-sdk-consumer-api-rate-plan-manager-card";

describe("RatePlanManagerCard", () => {
  it("renders plans", () => {
    const { container } = render(<RatePlanManagerCard />);
    expect(container.textContent).toContain("Rate Plan Manager");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("Enterprise");
  });

  it("shows pricing and limits", () => {
    const { container } = render(<RatePlanManagerCard />);
    expect(container.textContent).toContain("$29.99/mo");
    expect(container.textContent).toContain("300 req/min");
    expect(container.textContent).toContain("50 burst");
  });
});
