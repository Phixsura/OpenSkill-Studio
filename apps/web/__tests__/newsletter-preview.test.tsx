import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NewsletterPreview } from "@/components/newsletter-preview";

describe("NewsletterPreview", () => {
  const sections = [
    { heading: "What's New", body: "Dark mode launched!", cta_label: "Try it", cta_url: "/settings" },
  ];
  it("renders", () => {
    const { container } = render(
      <NewsletterPreview title="Dev Update" edition={42} sections={sections}
        onSend={vi.fn()} onEdit={vi.fn()} />
    );
    expect(container.textContent).toContain("Dev Update");
    expect(container.textContent).toContain("#42");
    expect(container.textContent).toContain("What's New");
    expect(container.textContent).toContain("Dark mode launched!");
    expect(container.textContent).toContain("Try it →");
  });
  it("send", () => {
    const fn = vi.fn();
    const { container } = render(
      <NewsletterPreview title="X" edition={1} sections={sections} onSend={fn} onEdit={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Send Newsletter")!);
    expect(fn).toHaveBeenCalled();
  });
});
