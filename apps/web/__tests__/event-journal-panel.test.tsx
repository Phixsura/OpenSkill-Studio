import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventJournalPanel } from "@/components/event-journal-panel";

const mockEvents = [
  { sequence: 1, eventType: "deploy", actor: "admin", timestamp: "12:00" },
  { sequence: 2, eventType: "config.changed", actor: "system", timestamp: "12:05" },
];
const mockStats = { totalEvents: 100, currentSequence: 100,
  eventTypes: { deploy: 30, "config.changed": 50, error: 20 } };

describe("EventJournalPanel", () => {
  it("renders events", () => {
    const { container } = render(<EventJournalPanel events={mockEvents} stats={mockStats} />);
    expect(container.textContent).toContain("#1");
    expect(container.textContent).toContain("deploy");
    expect(container.textContent).toContain("seq #100");
  });

  it("shows stats tab", () => {
    const { getByText, container } = render(<EventJournalPanel events={mockEvents} stats={mockStats} />);
    fireEvent.click(getByText("Stats"));
    expect(container.textContent).toContain("deploy");
    expect(container.textContent).toContain("30");
  });

  it("calls onReplay", () => {
    const onReplay = vi.fn();
    const { getByText } = render(<EventJournalPanel events={mockEvents} stats={mockStats} onReplay={onReplay} />);
    fireEvent.click(getByText("Replay All"));
    expect(onReplay).toHaveBeenCalledWith(1);
  });
});
