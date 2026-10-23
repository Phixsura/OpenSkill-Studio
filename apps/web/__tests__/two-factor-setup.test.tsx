import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TwoFactorSetup } from "@/components/two-factor-setup";

describe("TwoFactorSetup", () => {
  it("renders scan step", () => {
    const { container } = render(
      <TwoFactorSetup qrUri="otpauth://totp/Test?secret=abc" recoveryCodes={["ABCD1234"]}
        onVerify={vi.fn()} onComplete={vi.fn()} />
    );
    expect(container.textContent).toContain("Two-Factor Authentication");
    expect(container.textContent).toContain("Scan this QR code");
    expect(container.textContent).toContain("Next");
  });
});
