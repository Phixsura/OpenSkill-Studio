import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepHealthView } from "@/components/dep-health-view";

describe("DepHealthView", () => {
  it("renders", () => {
    const { container } = render(
      <DepHealthView healthPct={67} allHealthy={false} deps={[
        { name: "postgres", status: "healthy" },
        { name: "redis", status: "degraded" },
        { name: "external-api", status: "down" },
      ]} />
    );
    expect(container.textContent).toContain("Dependency Health");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("postgres");
    expect(container.textContent).toContain("redis");
    expect(container.textContent).toContain("down");
  });
});
