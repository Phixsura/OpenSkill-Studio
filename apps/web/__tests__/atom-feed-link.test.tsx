import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AtomFeedLink } from "@/components/atom-feed-link";

describe("AtomFeedLink", () => {
  it("renders", () => {
    const { container } = render(
      <AtomFeedLink appName="Auth SDK" feedUrl="https://x.com/feed" entryCount={5}
        onCopy={vi.fn()} onSubscribe={vi.fn()} />
    );
    expect(container.textContent).toContain("Auth SDK Atom Feed");
    expect(container.textContent).toContain("5 entries");
    expect(container.textContent).toContain("📡");
  });
  it("subscribe", () => {
    const fn = vi.fn();
    const { container } = render(
      <AtomFeedLink appName="X" feedUrl="x" entryCount={0} onCopy={vi.fn()} onSubscribe={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Subscribe")!);
    expect(fn).toHaveBeenCalled();
  });
});
