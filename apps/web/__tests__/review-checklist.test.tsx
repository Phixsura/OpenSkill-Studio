import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReviewChecklist } from "@/components/review-checklist";

const CHECKS = [
  { name: "manifest_valid", passed: true, message: "Valid manifest" },
  { name: "version_format", passed: true, message: "Valid semver" },
  { name: "content_hash", passed: false, message: "Missing hash" },
  { name: "high_risk", passed: true, message: "No high-risk", warning: true },
];

describe("ReviewChecklist", () => {
  it("renders all checks", () => {
    const { container } = render(<ReviewChecklist checks={CHECKS} score={75} passed={false} />);
    expect(container.textContent).toContain("manifest valid");
    expect(container.textContent).toContain("content hash");
  });

  it("shows score", () => {
    const { container } = render(<ReviewChecklist checks={CHECKS} score={75} passed={false} />);
    expect(container.textContent).toContain("75%");
  });

  it("shows passed status", () => {
    const { container } = render(<ReviewChecklist checks={[]} score={100} passed={true} />);
    expect(container.textContent).toContain("Passed");
  });

  it("shows failed status", () => {
    const { container } = render(<ReviewChecklist checks={CHECKS} score={75} passed={false} />);
    expect(container.textContent).toContain("Failed");
  });

  it("shows check icons", () => {
    const { container } = render(<ReviewChecklist checks={CHECKS} score={75} passed={false} />);
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
  });
});
