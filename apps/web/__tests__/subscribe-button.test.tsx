import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SubscribeButton } from "@/components/subscribe-button";

describe("SubscribeButton", () => {
  it("shows subscribed", () => {
    const { container } = render(<SubscribeButton subscribed={true} subscriberCount={42} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("Subscribed");
    expect(container.textContent).toContain("42");
  });
  it("shows unsubscribed", () => {
    const { container } = render(<SubscribeButton subscribed={false} subscriberCount={10} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("Subscribe");
  });
  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { container } = render(<SubscribeButton subscribed={false} subscriberCount={0} onToggle={onToggle} />);
    fireEvent.click(container.querySelector("button")!);
    expect(onToggle).toHaveBeenCalled();
  });
});
