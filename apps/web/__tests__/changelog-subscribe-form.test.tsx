import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogSubscribeForm } from "@/components/changelog-subscribe-form";

describe("ChangelogSubscribeForm", () => {
  it("renders and subscribes", () => {
    const onSub = vi.fn();
    const { container, getByPlaceholderText, getByText } = render(
      <ChangelogSubscribeForm onSubscribe={onSub} subscriberCount={1500} />
    );
    expect(container.textContent).toContain("Stay Updated");
    expect(container.textContent).toContain("1,500");
    fireEvent.change(getByPlaceholderText("you@example.com"), { target: { value: "test@test.com" } });
    fireEvent.click(getByText("Subscribe"));
    expect(onSub).toHaveBeenCalledWith("test@test.com", "weekly");
  });
});
