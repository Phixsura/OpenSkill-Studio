import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogSubManager } from "@/components/changelog-sub-manager";

describe("ChangelogSubManager", () => {
  it("renders subscribed state", () => {
    const { container } = render(
      <ChangelogSubManager active={10} total={15} currentChannel="email"
        byChannel={{ email: 7, slack: 3 }} onSubscribe={vi.fn()} onUnsubscribe={vi.fn()} />
    );
    expect(container.textContent).toContain("Changelog Subscriptions");
    expect(container.textContent).toContain("10 active");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("Unsubscribe");
  });
});
