import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventSimulatorPanel } from "@/components/event-simulator-panel";

describe("EventSimulatorPanel", () => {
  it("renders simulator", () => {
    const onSim = vi.fn();
    const { container, getByText } = render(
      <EventSimulatorPanel onSimulate={onSim}
        templates={[{ eventType: "app.installed", fields: ["app_id"] }, { eventType: "user.created", fields: ["user_id"] }]}
        lastResult={{ eventId: "evt_abc", success: true, statusCode: 200 }} />
    );
    expect(container.textContent).toContain("Event Simulator");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("evt_abc");
    fireEvent.click(getByText("Send"));
    expect(onSim).toHaveBeenCalledWith("app.installed");
  });
});
