import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AlertSettingsForm } from "@/components/alert-settings-form";

describe("AlertSettingsForm", () => {
  it("renders settings", () => {
    const onToggle = vi.fn();
    const { container, getByText, getAllByRole } = render(
      <AlertSettingsForm onSave={vi.fn()} onToggle={onToggle} alerts={[
        { metric: "error_rate", threshold: 5, unit: "%", channel: "email", enabled: true },
        { metric: "latency_p99", threshold: 1000, unit: "ms", channel: "slack", enabled: true },
      ]} />
    );
    expect(container.textContent).toContain("Alert Settings");
    expect(container.textContent).toContain("error rate");
    expect(container.textContent).toContain("5%");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("1000ms");
  });
});
