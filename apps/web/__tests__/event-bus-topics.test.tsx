import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventBusTopics } from "@/components/event-bus-topics";

describe("EventBusTopics", () => {
  const topics = [
    { name: "app.installed", subscribers: 5, events_24h: 120, avg_latency_ms: 15 },
  ];
  it("renders", () => {
    const { container } = render(
      <EventBusTopics topics={topics} totalEvents24h={120} onSubscribe={vi.fn()} />
    );
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("5 subscribers");
    expect(container.textContent).toContain("120 events");
  });
  it("subscribe", () => {
    const fn = vi.fn();
    const { container } = render(
      <EventBusTopics topics={topics} totalEvents24h={120} onSubscribe={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Subscribe")!);
    expect(fn).toHaveBeenCalledWith("app.installed");
  });
});
