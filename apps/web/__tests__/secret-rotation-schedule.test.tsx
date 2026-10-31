import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SecretRotationSchedule } from "@/components/secret-rotation-schedule";

describe("SecretRotationSchedule", () => {
  const schedule = [
    { secret_id: "s1", name: "API Key", age_days: 95, max_age_days: 90, needs_rotation: true, days_until_rotation: 0, urgency: "critical" },
    { secret_id: "s2", name: "Webhook", age_days: 30, max_age_days: 90, needs_rotation: false, days_until_rotation: 60, urgency: "ok" },
  ];
  it("renders", () => {
    const { container } = render(
      <SecretRotationSchedule schedule={schedule} overdueCount={1} onRotate={vi.fn()} />
    );
    expect(container.textContent).toContain("Secret Rotation");
    expect(container.textContent).toContain("1 overdue");
    expect(container.textContent).toContain("API Key");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("Rotate Now");
  });
  it("rotate", () => {
    const fn = vi.fn();
    const { container } = render(
      <SecretRotationSchedule schedule={schedule} overdueCount={1} onRotate={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Rotate Now")!);
    expect(fn).toHaveBeenCalledWith("s1");
  });
});
