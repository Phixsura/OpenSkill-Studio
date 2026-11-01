import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuickstartGuide } from "@/components/quickstart-guide";

describe("QuickstartGuide", () => {
  it("renders guide", () => {
    const sections = [
      { title: "Installation", content: "1. Click Install\n2. Configure" },
      { title: "Usage", content: "Start using the app" },
    ];
    const { container } = render(<QuickstartGuide appName="SuperApp" sections={sections} setupMinutes={5} />);
    expect(container.textContent).toContain("Getting Started with SuperApp");
    expect(container.textContent).toContain("5 minutes");
    expect(container.textContent).toContain("Installation");
  });
});
