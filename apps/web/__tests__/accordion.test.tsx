import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Accordion } from "@/components/accordion";

describe("Accordion", () => {
  const items = [
    { index: 0, title: "Getting Started", content: "Install SDK", icon: "🚀", open: true },
    { index: 1, title: "Config", content: "Set API key", icon: null, open: false },
  ];
  it("renders with first open", () => {
    const { container } = render(<Accordion items={items} allowMultiple={false} />);
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Install SDK");
    expect(container.textContent).toContain("Config");
    expect(container.textContent).not.toContain("Set API key");
  });
  it("toggles on click", () => {
    const { container } = render(<Accordion items={items} allowMultiple={false} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(container.textContent).toContain("Set API key");
  });
});
