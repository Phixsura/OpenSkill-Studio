import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FeatureFlagAuditCard from "../src/components/feature-flag-audit-card";

const entries = [
  { entry_id: "e1", flag_key: "dark_mode", action: "created", actor: "alice", reason: "" },
  {
    entry_id: "e2",
    flag_key: "dark_mode",
    action: "enabled",
    actor: "bob",
    reason: "Launch ready",
  },
  { entry_id: "e3", flag_key: "beta_ui", action: "disabled", actor: "alice", reason: "Bug found" },
];

describe("FeatureFlagAuditCard", () => {
  it("renders header and total", () => {
    const { container } = render(
      <FeatureFlagAuditCard entries={entries} totalCount={50} appName="App" />,
    );
    expect(container.textContent).toContain("Flag Audit Log");
    expect(container.textContent).toContain("50 events");
  });

  it("shows flag keys and actions", () => {
    const { container } = render(
      <FeatureFlagAuditCard entries={entries} totalCount={3} appName="App" />,
    );
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("enabled");
    expect(container.textContent).toContain("disabled");
  });

  it("shows actors", () => {
    const { container } = render(
      <FeatureFlagAuditCard entries={entries} totalCount={3} appName="App" />,
    );
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("bob");
  });

  it("shows reasons when present", () => {
    const { container } = render(
      <FeatureFlagAuditCard entries={entries} totalCount={3} appName="App" />,
    );
    expect(container.textContent).toContain("Launch ready");
    expect(container.textContent).toContain("Bug found");
  });

  it("shows empty state", () => {
    const { container } = render(
      <FeatureFlagAuditCard entries={[]} totalCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("No audit entries");
  });
});
