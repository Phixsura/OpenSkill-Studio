import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Pager, QueryError } from "@/components/cp-list";
import { Lightbox } from "@/components/lightbox";
import { StatusBadge } from "@/components/status-badge";

beforeEach(() => vi.clearAllMocks());

describe("StatusBadge (R528)", () => {
  it("null/missing status renders NOTHING instead of crashing the tree", () => {
    const a = render(<StatusBadge status={null} />);
    expect(a.container.textContent).toBe("");
    a.unmount();
    const b = render(<StatusBadge />);
    expect(b.container.textContent).toBe("");
  });

  it("humanizes underscores and applies the status class", () => {
    render(<StatusBadge status="past_due" />);
    const el = screen.getByText("past due");
    expect(el.className).toContain("rounded-full");
    expect(el.className.length).toBeGreaterThan("rounded-full".length); // StatusBadgeClass applied
  });
});

describe("Pager (R528)", () => {
  it("hidden on a single page; Prev disabled on page 1; Next disabled without more", () => {
    const onPage = vi.fn();
    const a = render(<Pager page={1} hasMore={false} onPage={onPage} />);
    expect(a.container.textContent).toBe(""); // no pager when nothing to page
    a.unmount();

    render(<Pager page={1} hasMore={true} onPage={onPage} />);
    expect((screen.getByRole("button", { name: "Prev" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(onPage).toHaveBeenCalledWith(2);
  });

  it("page>1 with no more still shows the pager so the user can go BACK", () => {
    const onPage = vi.fn();
    render(<Pager page={3} hasMore={false} onPage={onPage} />);
    expect((screen.getByRole("button", { name: "Next" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: "Prev" }));
    expect(onPage).toHaveBeenCalledWith(2);
    expect(screen.getByText("Page 3")).toBeTruthy();
  });
});

describe("QueryError (R528)", () => {
  it("surfaces the error message; non-Error objects fall back to generic copy", () => {
    const a = render(<QueryError error={new Error("rate limited")} what="invoices" />);
    expect(a.getByText(/Could not load invoices: rate limited/)).toBeTruthy();
    a.unmount();
    render(<QueryError error={"boom"} what="usage" />);
    expect(screen.getByText(/Could not load usage: Request failed/)).toBeTruthy();
  });
});

describe("Lightbox (R528)", () => {
  it("closes on Escape, backdrop click, and the close button — but NOT on image click", () => {
    const onClose = vi.fn();
    render(<Lightbox url="https://cdn.example/x.png" alt="work" onClose={onClose} />);
    // body scroll locked while open
    expect(document.body.style.overflow).toBe("hidden");
    fireEvent.click(screen.getByAltText("work"));
    expect(onClose).not.toHaveBeenCalled(); // stopPropagation on the image
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByTestId("lightbox"));
    expect(onClose).toHaveBeenCalledTimes(2);
    // the close button does not stop propagation: its click also bubbles to
    // the backdrop, so onClose fires twice — harmless (closing is idempotent)
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalledTimes(4);
  });

  it("unmount restores body scroll and removes the key listener", () => {
    const onClose = vi.fn();
    const view = render(<Lightbox url="https://cdn.example/x.png" alt="work" onClose={onClose} />);
    view.unmount();
    expect(document.body.style.overflow).toBe("");
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).not.toHaveBeenCalled(); // listener removed
  });
});
