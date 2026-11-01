import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-traffic-split-card";

describe("EndpointTrafficSplitCard", () => {
  it("shows targets", () => {
    const targets = [{ id: "v1", version: "1.0", weight: 90 }, { id: "v2", version: "2.0", weight: 10 }];
    const { container } = render(<Card endpointPath="/api/users" targets={targets} sticky={true} appName="App" />);
    expect(container.textContent).toContain("Traffic Split");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("10%");
    expect(container.textContent).toContain("Sticky");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpointPath="/api" targets={[]} sticky={false} appName="App" />);
    expect(container.textContent).toContain("No targets");
  });
});
