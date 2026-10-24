import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KeyRotationPanel } from "@/components/key-rotation-panel";
describe("KeyRotationPanel", () => {
  it("renders", () => {
    const { container } = render(
      <KeyRotationPanel overdue={1} rotationDays={90}
        keys={[
          { name: "db-password", ageDays: 100, dueInDays: 0, overdue: true },
          { name: "api-key", ageDays: 30, dueInDays: 60, overdue: false },
        ]} />
    );
    expect(container.textContent).toContain("Key Rotation");
    expect(container.textContent).toContain("1 overdue");
    expect(container.textContent).toContain("90d policy");
    expect(container.textContent).toContain("db-password");
    expect(container.textContent).toContain("ROTATE NOW");
    expect(container.textContent).toContain("60d left");
  });
});
