import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-ab-test-card";

describe("EndpointAbTestCard", () => {
  it("shows test", () => {
    const variants = [
      { id: "a", name: "Control", weightPct: 50, version: "v1", requests: 1000, errors: 5, avgMs: 50 },
      { id: "b", name: "Experiment", weightPct: 50, version: "v2", requests: 1000, errors: 20, avgMs: 80 },
    ];
    const { container } = render(<Card testId="t1" endpoint="/api/checkout" status="running" variants={variants} appName="App" />);
    expect(container.textContent).toContain("A/B Test");
    expect(container.textContent).toContain("Control");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("running");
  });
  it("shows empty", () => {
    const { container } = render(<Card testId="t1" endpoint="/api" status="draft" variants={[]} appName="App" />);
    expect(container.textContent).toContain("No variants");
  });
});
