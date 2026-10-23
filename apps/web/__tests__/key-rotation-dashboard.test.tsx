import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyRotationDashboard } from "@/components/key-rotation-dashboard";

describe("KeyRotationDashboard", () => {
  it("renders keys", () => {
    const onRotate = vi.fn();
    const { container, getByText } = render(
      <KeyRotationDashboard totalKeys={2} dueCount={1} onRotate={onRotate} keys={[
        { keyId: "k1", daysSinceRotation: 35, daysUntilDue: 0, due: true, urgency: "due" },
        { keyId: "k2", daysSinceRotation: 5, daysUntilDue: 25, due: false, urgency: "ok" },
      ]} />
    );
    expect(container.textContent).toContain("Key Rotation");
    expect(container.textContent).toContain("2 keys");
    expect(container.textContent).toContain("1 due");
    expect(container.textContent).toContain("k1");
    fireEvent.click(getByText("Rotate"));
    expect(onRotate).toHaveBeenCalledWith("k1");
  });
});
