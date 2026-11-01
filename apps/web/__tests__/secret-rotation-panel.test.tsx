import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SecretRotationPanel } from "@/components/secret-rotation-panel";

describe("SecretRotationPanel", () => {
  it("renders secrets", () => {
    const { container } = render(
      <SecretRotationPanel onRotate={vi.fn()} secrets={[
        { secretName: "API_KEY", ageDays: 80, dueInDays: 10, status: "warning", needsRotation: false },
        { secretName: "DB_PASS", ageDays: 95, dueInDays: 0, status: "overdue", needsRotation: true },
      ]} />
    );
    expect(container.textContent).toContain("Secret Rotation");
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("DB_PASS");
    expect(container.textContent).toContain("overdue");
    expect(container.textContent).toContain("Rotate");
  });
});
