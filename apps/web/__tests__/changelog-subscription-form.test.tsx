import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogSubscriptionForm } from "@/components/changelog-subscription-form";

describe("ChangelogSubscriptionForm", () => {
  it("renders", () => {
    const { container } = render(
      <ChangelogSubscriptionForm appName="MyApp" availableChannels={["email", "push", "slack"]}
        onSubscribe={vi.fn()} />
    );
    expect(container.textContent).toContain("Subscribe to MyApp Updates");
    expect(container.textContent).toContain("📧");
    expect(container.textContent).toContain("🔔");
    expect(container.textContent).toContain("1 channel");
  });
  it("subscribe", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChangelogSubscriptionForm appName="X" availableChannels={["email"]} onSubscribe={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Subscribe ("))!);
    expect(fn).toHaveBeenCalledWith(["email"]);
  });
});
