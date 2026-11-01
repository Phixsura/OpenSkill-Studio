import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperGuideCard from "../src/components/api-developer-guide-card";

const guides = [{ guide_id: "g1", title: "Getting Started", category: "quickstart", step_count: 3, view_count: 150 }];

describe("APIDeveloperGuideCard", () => {
  it("shows guides", () => {
    const { container } = render(<APIDeveloperGuideCard guides={guides} appName="App" />);
    expect(container.textContent).toContain("Developer Guides");
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("quickstart");
    expect(container.textContent).toContain("3 steps");
    expect(container.textContent).toContain("150 views");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperGuideCard guides={[]} appName="App" />);
    expect(container.textContent).toContain("No guides");
  });
});
