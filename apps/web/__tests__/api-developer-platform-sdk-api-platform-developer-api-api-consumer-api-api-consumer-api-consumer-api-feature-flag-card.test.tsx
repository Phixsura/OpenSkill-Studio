import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-feature-flag-card";

describe("ConsumerApiFeatureFlagCard", () => {
  it("shows flags", () => {
    const flags = [{ id: "dark", name: "Dark Mode", enabled: true, hasOverride: false, rolloutPct: 100 }, { id: "beta", name: "Beta", enabled: false, hasOverride: true, rolloutPct: 0 }];
    const { container } = render(<Card flags={flags} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("ON");
    expect(container.textContent).toContain("OFF");
    expect(container.textContent).toContain("override");
    expect(container.textContent).toContain("1/2 enabled");
  });
  it("shows empty", () => {
    const { container } = render(<Card flags={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No feature flags");
  });
});
