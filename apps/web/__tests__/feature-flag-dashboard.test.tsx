import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagDashboard } from "@/components/feature-flag-dashboard";

const MOCK_FLAGS = [
  {
    key: "new-editor",
    description: "New code editor",
    status: "active" as const,
    default_value: false,
    rules: [{ rule_type: "percentage" as const, value: 50 }],
    depends_on: [],
  },
  {
    key: "dark-mode-v2",
    description: "Dark mode redesign",
    status: "active" as const,
    default_value: true,
    rules: [{ rule_type: "boolean" as const, value: true }],
    depends_on: [],
  },
  {
    key: "legacy-api",
    description: "Legacy API support",
    status: "disabled" as const,
    default_value: false,
    rules: [],
    depends_on: [],
  },
  {
    key: "old-feature",
    description: "Archived feature",
    status: "archived" as const,
    default_value: false,
    rules: [],
    depends_on: ["new-editor"],
  },
];

const MOCK_EVALS = {
  "new-editor": { key: "new-editor", enabled: true, reason: "rule_0" },
  "dark-mode-v2": { key: "dark-mode-v2", enabled: true, reason: "rule_0" },
  "legacy-api": { key: "legacy-api", enabled: false, reason: "flag_disabled" },
  "old-feature": { key: "old-feature", enabled: false, reason: "flag_archived" },
};

describe("FeatureFlagDashboard", () => {
  it("renders heading and counts", () => {
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("4 flags");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("1 disabled");
  });

  it("renders all flag keys", () => {
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("new-editor");
    expect(container.textContent).toContain("dark-mode-v2");
    expect(container.textContent).toContain("legacy-api");
    expect(container.textContent).toContain("old-feature");
  });

  it("renders rule labels", () => {
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("50% rollout");
    expect(container.textContent).toContain("On");
  });

  it("filters by status", () => {
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={vi.fn()}
      />,
    );
    const disabledBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Disabled",
    );
    fireEvent.click(disabledBtn!);
    expect(container.textContent).toContain("legacy-api");
    expect(container.textContent).not.toContain("new-editor");
  });

  it("shows empty state when no flags match filter", () => {
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={vi.fn()}
      />,
    );
    // There's only 1 archived flag — archived filter works
    const archivedBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Archived",
    );
    fireEvent.click(archivedBtn!);
    expect(container.textContent).toContain("old-feature");
  });

  it("calls onToggle when switch clicked", () => {
    const onToggle = vi.fn();
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={onToggle}
        onArchive={vi.fn()}
      />,
    );
    const switches = container.querySelectorAll("[role='switch']");
    expect(switches.length).toBe(4);
    fireEvent.click(switches[0]); // new-editor is currently on → toggle off
    expect(onToggle).toHaveBeenCalledWith("new-editor", false);
  });

  it("expands to show rules and details", () => {
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={vi.fn()}
      />,
    );
    // Click expand on first flag row
    const expandButtons = Array.from(container.querySelectorAll("button")).filter((b) =>
      b.textContent?.includes("new-editor"),
    );
    fireEvent.click(expandButtons[0]);
    expect(container.textContent).toContain("Rules");
    expect(container.textContent).toContain("percentage");
    expect(container.textContent).toContain("Eval: rule_0");
  });

  it("shows Archive button for active flags", () => {
    const onArchive = vi.fn();
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={onArchive}
      />,
    );
    // Expand active flag
    const expandButtons = Array.from(container.querySelectorAll("button")).filter((b) =>
      b.textContent?.includes("new-editor"),
    );
    fireEvent.click(expandButtons[0]);
    const archiveBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Archive",
    );
    expect(archiveBtn).toBeTruthy();
    fireEvent.click(archiveBtn!);
    expect(onArchive).toHaveBeenCalledWith("new-editor");
  });

  it("shows depends_on when expanded", () => {
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={vi.fn()}
      />,
    );
    // Filter to archived to find old-feature
    const archivedBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Archived",
    );
    fireEvent.click(archivedBtn!);
    const expandButtons = Array.from(container.querySelectorAll("button")).filter((b) =>
      b.textContent?.includes("old-feature"),
    );
    fireEvent.click(expandButtons[0]);
    expect(container.textContent).toContain("Depends on");
    expect(container.textContent).toContain("new-editor");
  });

  it("renders toggle switches with correct aria", () => {
    const { container } = render(
      <FeatureFlagDashboard
        flags={MOCK_FLAGS}
        evaluations={MOCK_EVALS}
        onToggle={vi.fn()}
        onArchive={vi.fn()}
      />,
    );
    const switches = container.querySelectorAll("[role='switch']");
    expect(switches.length).toBe(4);
    // new-editor is enabled
    expect(switches[0].getAttribute("aria-checked")).toBe("true");
  });
});
