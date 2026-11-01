import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EventBusCard from "../src/components/api-developer-platform-sdk-consumer-api-event-bus-card";

describe("EventBusCard", () => {
  it("renders title and subscriptions", () => {
    const { container } = render(<EventBusCard />);
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("order.*");
    expect(container.textContent).toContain("user.created");
  });

  it("shows event stats", () => {
    const { container } = render(<EventBusCard />);
    expect(container.textContent).toContain("4,500 events");
    expect(container.textContent).toContain("12 topics");
  });
});
