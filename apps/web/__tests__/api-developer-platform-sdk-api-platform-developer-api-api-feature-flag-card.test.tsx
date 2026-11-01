import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-feature-flag-card";

describe("FeatureFlagCard", () => {
  it("shows flags", () => {
    const flags = [{ flag_id: "f1", name: "New UI", enabled: true, rollout_pct: 50, allowlist_count: 3 }];
    const { container } = render(<Card flags={flags} appName="App" />);
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("New UI");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("+3");
  });
  it("shows empty", () => {
    const { container } = render(<Card flags={[]} appName="App" />);
    expect(container.textContent).toContain("No feature flags");
  });
});
