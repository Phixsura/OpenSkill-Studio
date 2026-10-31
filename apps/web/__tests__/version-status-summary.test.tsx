import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionStatusSummary } from "@/components/version-status-summary";

describe("VersionStatusSummary", () => {
  it("shows counts", () => {
    const { container } = render(<VersionStatusSummary total={5} approved={3} pending={1} rejected={1} latestVersion="2.0" hasPending={true} />);
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("v2.0");
  });
  it("shows pending warning", () => {
    const { container } = render(<VersionStatusSummary total={1} approved={0} pending={1} rejected={0} latestVersion="1.0" hasPending={true} />);
    expect(container.textContent).toContain("Review in progress");
  });
  it("no warning when no pending", () => {
    const { container } = render(<VersionStatusSummary total={2} approved={2} pending={0} rejected={0} latestVersion="2.0" hasPending={false} />);
    expect(container.textContent).not.toContain("Review in progress");
  });
});
