import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogSubscribeToggle } from "@/components/changelog-subscribe-toggle";

describe("ChangelogSubscribeToggle", () => {
  it("renders subscribed", () => {
    const onToggle = vi.fn();
    const { container, getByText } = render(
      <ChangelogSubscribeToggle appName="App1" subscribed={true}
        subscriberCount={150} onToggle={onToggle} />
    );
    expect(container.textContent).toContain("Subscribed");
    expect(container.textContent).toContain("150 subscribers");
    fireEvent.click(getByText("Subscribed"));
    expect(onToggle).toHaveBeenCalled();
  });

  it("renders unsubscribed", () => {
    const { container } = render(
      <ChangelogSubscribeToggle appName="App1" subscribed={false}
        subscriberCount={42} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("Subscribe to updates");
  });
});
