import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyRotationStatus } from "@/components/key-rotation-status";

describe("KeyRotationStatus", () => {
  it("renders status", () => {
    const { container } = render(
      <KeyRotationStatus actionNeeded={true} dueKeys={["old_key"]}
        upcomingKeys={["soon_key"]} onRotate={vi.fn()} />
    );
    expect(container.textContent).toContain("Key Rotation");
    expect(container.textContent).toContain("1 overdue");
    expect(container.textContent).toContain("old_key");
    expect(container.textContent).toContain("Rotate Now");
    expect(container.textContent).toContain("soon_key");
    expect(container.textContent).toContain("Upcoming");
  });
});
