import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MigrationPlanViewer } from "@/components/migration-plan-viewer";

const STEPS = [
  { action: "request_consent", reason: "New permissions: write:cohorts" },
  { action: "update_sandbox", reason: "Memory increased" },
  { action: "upgrade_installations", count: 10 },
];

describe("MigrationPlanViewer", () => {
  it("shows version range", () => {
    const { container } = render(<MigrationPlanViewer fromVersion="1.0" toVersion="2.0" breaking={false} steps={STEPS} affectedInstallations={10} requiresConsent={true} />);
    expect(container.textContent).toContain("1.0 → 2.0");
  });

  it("shows steps", () => {
    const { container } = render(<MigrationPlanViewer fromVersion="1.0" toVersion="2.0" breaking={false} steps={STEPS} affectedInstallations={10} requiresConsent={false} />);
    expect(container.textContent).toContain("request consent");
    expect(container.textContent).toContain("upgrade installations");
  });

  it("shows breaking badge", () => {
    const { container } = render(<MigrationPlanViewer fromVersion="1.0" toVersion="2.0" breaking={true} steps={STEPS} affectedInstallations={0} requiresConsent={false} />);
    expect(container.textContent).toContain("Breaking");
  });

  it("shows consent badge", () => {
    const { container } = render(<MigrationPlanViewer fromVersion="1.0" toVersion="2.0" breaking={false} steps={STEPS} affectedInstallations={0} requiresConsent={true} />);
    expect(container.textContent).toContain("Consent");
  });

  it("shows affected count", () => {
    const { container } = render(<MigrationPlanViewer fromVersion="1.0" toVersion="2.0" breaking={false} steps={STEPS} affectedInstallations={42} requiresConsent={false} />);
    expect(container.textContent).toContain("42 installations");
  });
});
