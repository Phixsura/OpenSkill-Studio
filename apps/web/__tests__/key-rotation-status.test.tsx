import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyRotationStatus } from "@/components/key-rotation-status";

describe("KeyRotationStatus", () => {
  it("renders grace period", () => {
    const { container } = render(
      <KeyRotationStatus newPrefix="osk_new1" oldPrefix="osk_old1"
        graceUntil="2026-02-01" status="in_grace_period" oldKeyActive={true} onRotate={vi.fn()} />
    );
    expect(container.textContent).toContain("Key Rotation");
    expect(container.textContent).toContain("osk_new1");
    expect(container.textContent).toContain("Grace period");
    expect(container.textContent).toContain("Rotate Again");
  });
});
