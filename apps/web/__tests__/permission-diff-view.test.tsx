import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PermissionDiffView } from "@/components/permission-diff-view";

describe("PermissionDiffView", () => {
  it("shows no changes", () => {
    const { container } = render(<PermissionDiffView added={[]} removed={[]} unchanged={["read:cohorts"]} breaking={false} needsConsent={false} />);
    expect(container.textContent).toContain("No permission changes");
  });

  it("shows added", () => {
    const { container } = render(<PermissionDiffView added={["write:cohorts"]} removed={[]} unchanged={[]} breaking={false} needsConsent={true} />);
    expect(container.textContent).toContain("write:cohorts");
    expect(container.textContent).toContain("Added");
  });

  it("shows removed", () => {
    const { container } = render(<PermissionDiffView added={[]} removed={["read:old"]} unchanged={[]} breaking={true} needsConsent={false} />);
    expect(container.textContent).toContain("read:old");
    expect(container.textContent).toContain("Breaking");
  });

  it("shows consent badge", () => {
    const { container } = render(<PermissionDiffView added={["read:new"]} removed={[]} unchanged={[]} breaking={false} needsConsent={true} />);
    expect(container.textContent).toContain("Consent");
  });
});
