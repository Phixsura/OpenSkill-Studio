import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CompatibilityMatrixView } from "@/components/compatibility-matrix-view";

const MOCK_IMPACT = {
  platform_version: "3.0",
  compatible: [
    {
      app_id: "app-1",
      app_version: "2.0.0",
      platform_version: "3.0",
      status: "compatible" as const,
      notes: "",
    },
  ],
  degraded: [
    {
      app_id: "app-2",
      app_version: "1.0.0",
      platform_version: "3.0",
      status: "degraded" as const,
      notes: "Minor UI issues",
    },
  ],
  incompatible: [
    {
      app_id: "app-3",
      app_version: "1.0.0",
      platform_version: "3.0",
      status: "incompatible" as const,
      notes: "API removed",
    },
  ],
  untested: ["app-4"],
  safe_to_upgrade: false,
};

const SAFE_IMPACT = {
  ...MOCK_IMPACT,
  incompatible: [],
  untested: [],
  safe_to_upgrade: true,
};

describe("CompatibilityMatrixView", () => {
  it("renders version transition", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("2.0 → 3.0");
  });

  it("renders apps affected count", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("4 apps affected");
  });

  it("shows Upgrade Blocked when unsafe", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("Upgrade Blocked");
  });

  it("shows Safe to Upgrade when safe", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={SAFE_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("Safe to Upgrade");
  });

  it("renders summary counts", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("1 compatible");
    expect(container.textContent).toContain("1 degraded");
    expect(container.textContent).toContain("1 incompatible");
    expect(container.textContent).toContain("1 untested");
  });

  it("renders incompatible apps", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("app-3");
    expect(container.textContent).toContain("API removed");
    expect(container.textContent).toContain("must upgrade");
  });

  it("renders degraded apps", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("app-2");
    expect(container.textContent).toContain("Minor UI issues");
  });

  it("renders untested app ids", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("app-4");
  });

  it("renders compatible apps", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("app-1");
    expect(container.textContent).toContain("v2.0.0");
  });

  it("renders status badges", () => {
    const { container } = render(
      <CompatibilityMatrixView impact={MOCK_IMPACT} currentPlatform="2.0" />,
    );
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("⚠");
    expect(container.textContent).toContain("✗");
  });

  it("shows empty state", () => {
    const empty = {
      ...MOCK_IMPACT,
      compatible: [],
      degraded: [],
      incompatible: [],
      untested: [],
      safe_to_upgrade: true,
    };
    const { container } = render(<CompatibilityMatrixView impact={empty} currentPlatform="2.0" />);
    expect(container.textContent).toContain("No installed apps");
  });
});
