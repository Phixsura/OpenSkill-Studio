import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InterServicePanel } from "@/components/inter-service-panel";

const mockMessages = [
  { id: "m1", fromExtension: "ext-a", toExtension: "ext-b", messageType: "request" as const,
    channel: "data", status: "delivered" as const, timestamp: "" },
  { id: "m2", fromExtension: "ext-b", toExtension: "ext-a", messageType: "response" as const,
    channel: "data", status: "delivered" as const, timestamp: "" },
];
const mockChannels = [
  { channel: "data", subscribed: true },
  { channel: "events", subscribed: false },
];

describe("InterServicePanel", () => {
  it("renders messages", () => {
    const { container } = render(
      <InterServicePanel messages={mockMessages} channels={mockChannels} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("ext-a");
    expect(container.textContent).toContain("2 messages");
  });

  it("shows channels with subscribe", () => {
    const onSubscribe = vi.fn();
    const { getByText } = render(
      <InterServicePanel messages={[]} channels={mockChannels} extensionName="Test" onSubscribe={onSubscribe} />
    );
    fireEvent.click(getByText("Channels (2)"));
    fireEvent.click(getByText("Subscribe"));
    expect(onSubscribe).toHaveBeenCalledWith("events");
  });

  it("shows subscribed indicator", () => {
    const { getByText, container } = render(
      <InterServicePanel messages={[]} channels={mockChannels} extensionName="Test" />
    );
    fireEvent.click(getByText("Channels (2)"));
    expect(container.textContent).toContain("subscribed");
  });
});
