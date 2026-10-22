import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionDiff } from "@/components/version-diff";

const COMPATIBLE_DIFF = {
  version_from: "1.0.0", version_to: "1.1.0", breaking: false,
  permissions: { added: ["write:cohorts"], removed: [] },
  events: { added: ["cohort.member_added"], removed: [] },
  secrets: { added: [], removed: [] },
  ui_extensions: { added: [], removed: [] },
  sandbox: { changed: false },
  config_schema_changed: false,
  summary: "+1 permissions; +1 event subscriptions",
};

const BREAKING_DIFF = {
  version_from: "2.0.0", version_to: "1.0.0", breaking: true,
  permissions: { added: [], removed: ["write:cohorts", "subscribe:events"] },
  events: { added: [], removed: [] },
  secrets: { added: [], removed: [] },
  ui_extensions: { added: [], removed: [] },
  sandbox: { changed: true },
  config_schema_changed: true,
  summary: "-2 permissions (BREAKING); sandbox config changed",
};

describe("VersionDiff", () => {
  it("renders compatible diff", () => {
    const { container } = render(<VersionDiff diff={COMPATIBLE_DIFF} />);
    expect(container.textContent).toContain("1.0.0");
    expect(container.textContent).toContain("1.1.0");
    expect(container.textContent).toContain("Compatible");
  });

  it("renders breaking diff", () => {
    const { container } = render(<VersionDiff diff={BREAKING_DIFF} />);
    expect(container.textContent).toContain("Breaking");
  });

  it("shows added permissions", () => {
    const { container } = render(<VersionDiff diff={COMPATIBLE_DIFF} />);
    expect(container.textContent).toContain("write:cohorts");
  });

  it("shows removed permissions", () => {
    const { container } = render(<VersionDiff diff={BREAKING_DIFF} />);
    expect(container.textContent).toContain("write:cohorts");
    expect(container.textContent).toContain("subscribe:events");
  });

  it("shows sandbox changed", () => {
    const { container } = render(<VersionDiff diff={BREAKING_DIFF} />);
    expect(container.textContent).toContain("Sandbox");
  });

  it("shows config schema changed", () => {
    const { container } = render(<VersionDiff diff={BREAKING_DIFF} />);
    expect(container.textContent).toContain("Config schema");
  });

  it("shows summary", () => {
    const { container } = render(<VersionDiff diff={COMPATIBLE_DIFF} />);
    expect(container.textContent).toContain("permissions");
  });
});
