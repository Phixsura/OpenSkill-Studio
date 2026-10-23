import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogSubscribeForm } from "@/components/changelog-subscribe-form";

describe("ChangelogSubscribeForm", () => {
  it("renders form", () => {
    const { container } = render(
      <ChangelogSubscribeForm appName="SuperApp" channels={["email", "slack", "rss"]} onSubscribe={vi.fn()} />
    );
    expect(container.textContent).toContain("Subscribe to SuperApp Updates");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("Subscribe");
  });
});
