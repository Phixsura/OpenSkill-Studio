import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VerificationBadge } from "@/components/verification-badge";

describe("VerificationBadge", () => {
  it("renders trusted", () => {
    const { container } = render(<VerificationBadge level="trusted" />);
    expect(container.textContent).toContain("Trusted Developer");
    expect(container.textContent).toContain("⭐");
  });
  it("renders verified", () => {
    const { container } = render(<VerificationBadge level="verified" />);
    expect(container.textContent).toContain("Verified Developer");
  });
  it("renders nothing for none", () => {
    const { container } = render(<VerificationBadge level="none" />);
    expect(container.textContent).toBe("");
  });
  it("hides label", () => {
    const { container } = render(<VerificationBadge level="basic" showLabel={false} />);
    expect(container.textContent).not.toContain("Email Verified");
  });
});
