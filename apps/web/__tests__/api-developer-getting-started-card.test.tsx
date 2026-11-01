import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperGettingStartedCard from "../src/components/api-developer-getting-started-card";

const sections = [
  { section_id: "s1", title: "Install SDK", has_code: true, language: "bash" },
  { section_id: "s2", title: "Setup Auth", has_code: true, language: "javascript" },
];

describe("APIDeveloperGettingStartedCard", () => {
  it("shows sections", () => {
    const { container } = render(<APIDeveloperGettingStartedCard sections={sections} appName="App" />);
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Install SDK");
    expect(container.textContent).toContain("bash");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperGettingStartedCard sections={[]} appName="App" />);
    expect(container.textContent).toContain("No getting started content");
  });
});
