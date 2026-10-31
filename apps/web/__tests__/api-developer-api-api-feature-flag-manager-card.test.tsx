import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiFeatureFlagManagerCard from "../src/components/api-developer-api-api-feature-flag-manager-card";

const flags = [
  { flag_id: "f1", name: "Dark Mode", enabled: true, rollout_pct: 50, evaluation_count: 5000 },
  { flag_id: "f2", name: "New Checkout", enabled: false, rollout_pct: 0, evaluation_count: 0 },
];

describe("APIDeveloperAPIApiFeatureFlagManagerCard", () => {
  it("shows flags", () => {
    const { container } = render(<APIDeveloperAPIApiFeatureFlagManagerCard flags={flags} appName="App" />);
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("1/2 enabled");
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("5,000 evals");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiFeatureFlagManagerCard flags={[]} appName="App" />);
    expect(container.textContent).toContain("No feature flags");
  });
});
