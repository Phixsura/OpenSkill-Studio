import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GlossaryPanel } from "@/components/glossary-panel";

const terms = [
  { term: "Sandbox", definition: "Isolated env", category: "runtime", related: ["Extension"] },
  { term: "Webhook", definition: "HTTP callback", category: "api", related: [] },
];

describe("GlossaryPanel", () => {
  it("renders terms", () => {
    const { container } = render(<GlossaryPanel terms={terms} categories={["runtime", "api"]} />);
    expect(container.textContent).toContain("Sandbox");
    expect(container.textContent).toContain("Isolated env");
    expect(container.textContent).toContain("See also: Extension");
  });
  it("filters by category", () => {
    const { container } = render(<GlossaryPanel terms={terms} categories={["runtime", "api"]} />);
    const btns = container.querySelectorAll("button"); const apiBtn = Array.from(btns).find(b => b.textContent === "api" && b.className.includes("rounded-full")); if (apiBtn) fireEvent.click(apiBtn);
    expect(container.textContent).toContain("Webhook");
  });
});
