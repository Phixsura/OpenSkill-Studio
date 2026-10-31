import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FeatureFlagCard from "../src/components/feature-flag-card";

const enabledFlag = {
  flag_id: "dark-mode",
  enabled: true,
  rollout_pct: 100,
  description: "Enable dark mode for users",
  force_enable_count: 2,
  force_disable_count: 0,
};

const partialRollout = {
  flag_id: "new-dashboard",
  enabled: true,
  rollout_pct: 30,
  description: "Redesigned dashboard",
  force_enable_count: 0,
  force_disable_count: 1,
};

const disabledFlag = {
  flag_id: "beta-api",
  enabled: false,
  rollout_pct: 0,
  description: "",
  force_enable_count: 0,
  force_disable_count: 0,
};

describe("FeatureFlagCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<FeatureFlagCard flags={[enabledFlag]} appName="My App" />);
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("My App");
  });

  it("shows enabled count", () => {
    const { container } = render(
      <FeatureFlagCard flags={[enabledFlag, disabledFlag]} appName="App" />,
    );
    expect(container.textContent).toContain("1/2 enabled");
  });

  it("renders flag ids", () => {
    const { container } = render(
      <FeatureFlagCard flags={[enabledFlag, partialRollout]} appName="App" />,
    );
    expect(container.textContent).toContain("dark-mode");
    expect(container.textContent).toContain("new-dashboard");
  });

  it("shows description", () => {
    const { container } = render(<FeatureFlagCard flags={[enabledFlag]} appName="App" />);
    expect(container.textContent).toContain("Enable dark mode for users");
  });

  it("shows full rollout label", () => {
    const { container } = render(<FeatureFlagCard flags={[enabledFlag]} appName="App" />);
    expect(container.textContent).toContain("Full rollout");
  });

  it("shows partial rollout percentage", () => {
    const { container } = render(<FeatureFlagCard flags={[partialRollout]} appName="App" />);
    expect(container.textContent).toContain("30%");
  });

  it("shows off label for disabled flags", () => {
    const { container } = render(<FeatureFlagCard flags={[disabledFlag]} appName="App" />);
    expect(container.textContent).toContain("off");
  });

  it("shows force override counts", () => {
    const { container } = render(
      <FeatureFlagCard flags={[enabledFlag, partialRollout]} appName="App" />,
    );
    expect(container.textContent).toContain("2 forced on");
    expect(container.textContent).toContain("1 forced off");
  });

  it("shows empty state", () => {
    const { container } = render(<FeatureFlagCard flags={[]} appName="App" />);
    expect(container.textContent).toContain("No flags configured");
  });
});
