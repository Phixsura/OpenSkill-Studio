import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationPreferencesForm } from "@/components/notification-preferences-form";

describe("NotificationPreferencesForm", () => {
  it("renders table", () => {
    const prefs = { "error.spike": { channels: ["email"], enabled: true } };
    const labels = { "error.spike": "Error Spike" };
    const { container } = render(
      <NotificationPreferencesForm preferences={prefs} eventLabels={labels}
        channels={["email", "slack"]} onUpdate={vi.fn()} />
    );
    expect(container.textContent).toContain("Error Spike");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("slack");
    expect(container.querySelectorAll("input[type='checkbox']").length).toBe(3); // enabled + 2 channels
  });
});
