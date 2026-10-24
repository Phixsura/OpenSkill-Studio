import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventTypeBrowser } from "@/components/event-type-browser";

describe("EventTypeBrowser", () => {
  it("renders events", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <EventTypeBrowser selectedGroup={null} onSelectGroup={onSelect}
        groups={["app", "user"]} events={[
          { type: "app.installed", description: "App installed", category: "lifecycle" },
          { type: "user.created", description: "New user", category: "identity" },
        ]} />
    );
    expect(container.textContent).toContain("Event Types");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("user.created");
    expect(container.textContent).toContain("2 event types");
    fireEvent.click(getByText("app"));
    expect(onSelect).toHaveBeenCalledWith("app");
  });
});
