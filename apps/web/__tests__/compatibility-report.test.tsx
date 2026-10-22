import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CompatibilityReport } from "@/components/compatibility-report";

const COMPATIBLE_REPORT = {
  from_version: "1.0.0",
  to_version: "1.1.0",
  compatible: true,
  breaking_changes: [],
  warnings: ["New permission: write:cohorts"],
  permissions_added: ["write:cohorts"],
  permissions_removed: [],
};

const BREAKING_REPORT = {
  from_version: "1.0.0",
  to_version: "2.0.0",
  compatible: false,
  breaking_changes: ["Removed endpoint /api/v1/legacy"],
  warnings: [],
  permissions_added: [],
  permissions_removed: ["read:legacy"],
};

describe("CompatibilityReport", () => {
  it("renders compatible report", () => {
    const { container } = render(<CompatibilityReport report={COMPATIBLE_REPORT} />);
    expect(container.textContent).toContain("1.0.0");
    expect(container.textContent).toContain("1.1.0");
  });

  it("shows green for compatible", () => {
    const { container } = render(<CompatibilityReport report={COMPATIBLE_REPORT} />);
    const div = container.firstElementChild;
    expect(div?.className).toContain("green");
  });

  it("shows red for breaking", () => {
    const { container } = render(<CompatibilityReport report={BREAKING_REPORT} />);
    const div = container.firstElementChild;
    expect(div?.className).toContain("red");
  });

  it("lists breaking changes", () => {
    const { container } = render(<CompatibilityReport report={BREAKING_REPORT} />);
    expect(container.textContent).toContain("Removed endpoint");
  });

  it("lists warnings", () => {
    const { container } = render(<CompatibilityReport report={COMPATIBLE_REPORT} />);
    expect(container.textContent).toContain("write:cohorts");
  });
});
