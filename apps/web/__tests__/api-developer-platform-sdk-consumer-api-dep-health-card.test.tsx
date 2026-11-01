import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DepHealthCard from "../src/components/api-developer-platform-sdk-consumer-api-dep-health-card";

describe("DepHealthCard", () => {
  it("renders title and dependencies", () => {
    const { container } = render(<DepHealthCard />);
    expect(container.textContent).toContain("Dependency Health");
    expect(container.textContent).toContain("PostgreSQL");
    expect(container.textContent).toContain("RabbitMQ");
  });

  it("shows health count", () => {
    const { container } = render(<DepHealthCard />);
    expect(container.textContent).toContain("3/4 healthy");
  });
});
