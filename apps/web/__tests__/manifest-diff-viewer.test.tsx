import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ManifestDiffViewer } from "@/components/manifest-diff-viewer";

const MOCK_DIFF = {
  from_version: "1.0.0",
  to_version: "2.0.0",
  changes: [
    {
      field_path: "name",
      kind: "unchanged" as const,
      severity: "none" as const,
      old_value: "App",
      new_value: "App",
    },
    {
      field_path: "description",
      kind: "modified" as const,
      severity: "patch" as const,
      old_value: "Old desc",
      new_value: "New desc",
    },
    {
      field_path: "min_platform_version",
      kind: "modified" as const,
      severity: "breaking" as const,
      old_value: "1.0.0",
      new_value: "2.0.0",
    },
    {
      field_path: "changelog",
      kind: "added" as const,
      severity: "minor" as const,
      old_value: null,
      new_value: "Major update",
    },
    {
      field_path: "legacy_field",
      kind: "removed" as const,
      severity: "minor" as const,
      old_value: "old",
      new_value: null,
    },
  ],
  added_permissions: ["write:submissions"],
  removed_permissions: ["read:projects"],
  added_config_fields: ["batch_size"],
  removed_config_fields: ["timeout"],
  added_surfaces: ["ui_dashboard_widget"],
  removed_surfaces: [],
  has_breaking: true,
  summary: "4 changes (1 breaking), +1 permissions, -1 permissions",
};

const NO_CHANGES_DIFF = {
  ...MOCK_DIFF,
  changes: [
    {
      field_path: "name",
      kind: "unchanged" as const,
      severity: "none" as const,
      old_value: "App",
      new_value: "App",
    },
  ],
  has_breaking: false,
  added_permissions: [],
  removed_permissions: [],
  added_config_fields: [],
  removed_config_fields: [],
  added_surfaces: [],
  removed_surfaces: [],
  summary: "0 changes (0 breaking)",
};

describe("ManifestDiffViewer", () => {
  it("renders version transition", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("1.0.0 → 2.0.0");
  });

  it("renders summary", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("4 changes");
    expect(container.textContent).toContain("1 breaking");
  });

  it("shows breaking warning", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("breaking changes");
  });

  it("hides breaking warning when none", () => {
    const { container } = render(<ManifestDiffViewer diff={NO_CHANGES_DIFF} />);
    expect(container.textContent).not.toContain("breaking changes");
  });

  it("renders added permissions", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("write:submissions");
    expect(container.textContent).toContain("+Permissions");
  });

  it("renders removed permissions", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("read:projects");
    expect(container.textContent).toContain("−Permissions");
  });

  it("renders config field diffs", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("batch_size");
    expect(container.textContent).toContain("timeout");
  });

  it("renders surface diffs", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("ui_dashboard_widget");
  });

  it("renders modified field with old → new", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("Old desc");
    expect(container.textContent).toContain("New desc");
    expect(container.textContent).toContain("→");
  });

  it("renders severity badges", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("BREAKING");
    expect(container.textContent).toContain("PATCH");
  });

  it("renders added field value", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("Major update");
  });

  it("hides unchanged fields", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    // "name" is unchanged — should not appear in the diff list
    const items = container.querySelectorAll("[class*='bg-']");
    // name field should not have a change row
    expect(container.textContent).not.toMatch(/\+\s*name|−\s*name|~\s*name/);
  });

  it("shows no changes message", () => {
    const { container } = render(<ManifestDiffViewer diff={NO_CHANGES_DIFF} />);
    expect(container.textContent).toContain("No field changes");
  });

  it("renders change kind icons", () => {
    const { container } = render(<ManifestDiffViewer diff={MOCK_DIFF} />);
    expect(container.textContent).toContain("+"); // added
    expect(container.textContent).toContain("−"); // removed
    expect(container.textContent).toContain("~"); // modified
  });
});
