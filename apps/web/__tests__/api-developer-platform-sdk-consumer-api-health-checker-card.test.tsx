import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HealthCheckerCard from "../src/components/api-developer-platform-sdk-consumer-api-health-checker-card";

describe("HealthCheckerCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<HealthCheckerCard />);
    expect(container.textContent).toContain("Health Checker");
    expect(container.textContent).toContain("ep-auth");
    expect(container.textContent).toContain("ep-search");
    expect(container.textContent).toContain("ep-legacy");
  });

  it("shows circuit states and healthy count", () => {
    const { container } = render(<HealthCheckerCard />);
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("1/3 healthy");
  });
});
