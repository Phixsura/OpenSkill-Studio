import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WhatsNewPanel } from "@/components/whats-new-panel";

const items = [
  { date: "Oct 27", title: "600 Services!", description: "Milestone reached", type: "feature" as const },
  { date: "Oct 26", title: "Security fixes", description: "47 fixes applied", type: "fix" as const },
];

describe("WhatsNewPanel", () => {
  it("renders items", () => {
    const { container } = render(<WhatsNewPanel items={items} />);
    expect(container.textContent).toContain("600 Services!");
    expect(container.textContent).toContain("Oct 27");
    expect(container.textContent).toContain("47 fixes");
  });
});
