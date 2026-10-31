import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-geo-restriction-card";

describe("GeoRestrictionCard", () => {
  it("shows policies", () => {
    const policies = [{ consumer_id: "c1", mode: "allowlist", regions: ["US", "CA"], action: "block" }];
    const { container } = render(<Card policies={policies} appName="App" />);
    expect(container.textContent).toContain("Geo Restrictions");
    expect(container.textContent).toContain("allowlist");
    expect(container.textContent).toContain("US");
    expect(container.textContent).toContain("CA");
  });
  it("shows empty", () => {
    const { container } = render(<Card policies={[]} appName="App" />);
    expect(container.textContent).toContain("No geo restrictions");
  });
});
