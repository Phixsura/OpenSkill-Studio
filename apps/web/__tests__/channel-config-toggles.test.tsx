import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChannelConfigToggles } from "@/components/channel-config-toggles";

describe("ChannelConfigToggles", () => {
  it("renders channels", () => {
    const onToggle = vi.fn();
    const { container, getAllByRole } = render(
      <ChannelConfigToggles enabledCount={2} onToggle={onToggle} channels={[
        { id: "email", label: "Email", icon: "📧", enabled: true },
        { id: "slack", label: "Slack", icon: "💬", enabled: true },
        { id: "sms", label: "SMS", icon: "📱", enabled: false },
      ]} />
    );
    expect(container.textContent).toContain("Notification Channels");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("Email");
    expect(container.textContent).toContain("Slack");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onToggle).toHaveBeenCalledWith("email");
  });
});
