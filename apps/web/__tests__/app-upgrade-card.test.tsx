import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppUpgradeCard } from "@/components/app-upgrade-card";

const MINOR_PLAN = {
  from_version: "1.0.0",
  to_version: "1.1.0",
  compat_level: "minor_changes" as const,
  added_permissions: ["write:submissions"],
  removed_permissions: [],
  added_config: ["batch_size"],
  removed_config: [],
  breaking_reasons: [],
  requires_reauth: true,
  auto_migratable: true,
};

const BREAKING_PLAN = {
  from_version: "1.1.0",
  to_version: "2.0.0",
  compat_level: "breaking" as const,
  added_permissions: [],
  removed_permissions: ["read:projects"],
  added_config: [],
  removed_config: ["timeout"],
  breaking_reasons: ["Removed permissions: read:projects", "Removed config fields: timeout"],
  requires_reauth: false,
  auto_migratable: false,
};

const COMPATIBLE_PLAN = {
  from_version: "1.0.0",
  to_version: "1.0.1",
  compat_level: "compatible" as const,
  added_permissions: [],
  removed_permissions: [],
  added_config: [],
  removed_config: [],
  breaking_reasons: [],
  requires_reauth: false,
  auto_migratable: true,
};

describe("AppUpgradeCard", () => {
  it("renders app name and version transition", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="LMS Connector"
        appIcon="🔗"
        plan={MINOR_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("LMS Connector");
    expect(container.textContent).toContain("1.0.0 → 1.1.0");
  });

  it("renders Minor Changes badge", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={MINOR_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Minor Changes");
  });

  it("renders Breaking badge", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={BREAKING_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Breaking");
  });

  it("renders Compatible badge", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={COMPATIBLE_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Compatible");
  });

  it("shows breaking reasons", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={BREAKING_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Breaking Changes");
    expect(container.textContent).toContain("Removed permissions: read:projects");
  });

  it("shows added/removed permissions", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={MINOR_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("New Permissions");
    expect(container.textContent).toContain("write:submissions");
  });

  it("shows added config fields", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={MINOR_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("New Config Fields");
    expect(container.textContent).toContain("batch_size");
  });

  it("shows reauth notice", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={MINOR_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("permissions require your approval");
  });

  it("hides reauth notice when not needed", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={COMPATIBLE_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    expect(container.textContent).not.toContain("permissions require");
  });

  it("shows Force Upgrade for breaking", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={BREAKING_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Force Upgrade",
    );
    expect(btn).toBeTruthy();
  });

  it("shows Upgrade for non-breaking", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={MINOR_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
      />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Upgrade",
    );
    expect(btn).toBeTruthy();
  });

  it("calls onUpgrade", () => {
    const onUpgrade = vi.fn();
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={MINOR_PLAN}
        onUpgrade={onUpgrade}
        onDismiss={vi.fn()}
      />,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Upgrade")!,
    );
    expect(onUpgrade).toHaveBeenCalledOnce();
  });

  it("calls onDismiss", () => {
    const onDismiss = vi.fn();
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={MINOR_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={onDismiss}
      />,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Not Now")!,
    );
    expect(onDismiss).toHaveBeenCalledOnce();
  });

  it("shows upgrading state", () => {
    const { container } = render(
      <AppUpgradeCard
        appName="App"
        appIcon="📦"
        plan={MINOR_PLAN}
        onUpgrade={vi.fn()}
        onDismiss={vi.fn()}
        upgrading
      />,
    );
    expect(container.textContent).toContain("Upgrading…");
  });
});
