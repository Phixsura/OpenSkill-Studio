import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StateMachinePanel } from "@/components/state-machine-panel";

const mockMachine = {
  machineId: "sm-1", name: "Order Flow",
  currentState: "submitted",
  states: ["draft", "submitted", "processing", "shipped", "delivered"],
  availableEvents: ["process", "cancel"],
  history: [
    { fromState: "draft", toState: "submitted", event: "submit", timestamp: "12:00" },
  ],
};

describe("StateMachinePanel", () => {
  it("renders current state", () => {
    const { container } = render(<StateMachinePanel machine={mockMachine} />);
    expect(container.textContent).toContain("Order Flow");
    expect(container.textContent).toContain("submitted");
  });

  it("shows available events as buttons", () => {
    const onSend = vi.fn();
    const { getByText } = render(<StateMachinePanel machine={mockMachine} onSendEvent={onSend} />);
    fireEvent.click(getByText("process"));
    expect(onSend).toHaveBeenCalledWith("process");
  });

  it("shows all states with current highlighted", () => {
    const { container } = render(<StateMachinePanel machine={mockMachine} />);
    expect(container.textContent).toContain("draft");
    expect(container.textContent).toContain("● submitted");
    expect(container.textContent).toContain("delivered");
  });

  it("shows transition history", () => {
    const { getByText, container } = render(<StateMachinePanel machine={mockMachine} />);
    fireEvent.click(getByText("History (1)"));
    expect(container.textContent).toContain("draft");
    expect(container.textContent).toContain("→ submit");
  });
});
