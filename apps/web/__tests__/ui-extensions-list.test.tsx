import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UiExtensionsList } from "@/components/ui-extensions-list";

describe("UiExtensionsList", () => {
  it("shows extensions", () => {
    const { container } = render(<UiExtensionsList extensions={[{ surface: "dashboard_card", title: "Stats Card", entryPath: "card.html" }]} />);
    expect(container.textContent).toContain("Stats Card");
    expect(container.textContent).toContain("dashboard_card");
  });
  it("empty state", () => {
    const { container } = render(<UiExtensionsList extensions={[]} />);
    expect(container.textContent).toContain("No UI extensions");
  });
});
