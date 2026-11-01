import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventEmitterPanel } from "@/components/event-emitter-panel";

const mockListeners = [
  { listenerId: "l1", eventPattern: "user:*", handlerName: "handle_user", once: false, callCount: 15 },
  { listenerId: "l2", eventPattern: "init", handlerName: "setup", once: true, callCount: 1 },
];
const mockHistory = [
  { eventName: "user:created", listenersNotified: 1 },
  { eventName: "user:deleted", listenersNotified: 1 },
];

describe("EventEmitterPanel", () => {
  it("renders listeners", () => {
    const { container } = render(<EventEmitterPanel listeners={mockListeners} history={mockHistory} />);
    expect(container.textContent).toContain("user:*");
    expect(container.textContent).toContain("handle_user");
    expect(container.textContent).toContain("once");
  });

  it("calls onEmit", () => {
    const onEmit = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <EventEmitterPanel listeners={[]} history={[]} onEmit={onEmit} />
    );
    fireEvent.change(getByPlaceholderText("event:name"), { target: { value: "test:fire" } });
    fireEvent.click(getByText("Emit"));
    expect(onEmit).toHaveBeenCalledWith("test:fire");
  });

  it("shows event history", () => {
    const { getByText, container } = render(
      <EventEmitterPanel listeners={mockListeners} history={mockHistory} />
    );
    fireEvent.click(getByText("History (2)"));
    expect(container.textContent).toContain("user:created");
    expect(container.textContent).toContain("1 notified");
  });
});
