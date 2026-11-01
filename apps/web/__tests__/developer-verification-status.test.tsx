import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperVerificationStatus } from "@/components/developer-verification-status";

describe("DeveloperVerificationStatus", () => {
  it("shows verified", () => {
    const { container } = render(<DeveloperVerificationStatus verified={true} email="dev@x.com" />);
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("✅");
  });

  it("shows unverified with button", () => {
    const onVerify = vi.fn();
    const { container } = render(<DeveloperVerificationStatus verified={false} email="dev@x.com" onVerify={onVerify} />);
    expect(container.textContent).toContain("Unverified");
    fireEvent.click(container.querySelector("button")!);
    expect(onVerify).toHaveBeenCalled();
  });

  it("shows email", () => {
    const { container } = render(<DeveloperVerificationStatus verified={true} email="test@example.com" />);
    expect(container.textContent).toContain("test@example.com");
  });

  it("hides button when verified", () => {
    const { container } = render(<DeveloperVerificationStatus verified={true} email="x@y.com" />);
    expect(container.querySelector("button")).toBeNull();
  });
});
