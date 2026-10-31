import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-api-consumer-api-api-consumer-api-api-consumer-api-api-consumer-api-getting-started-card";

describe("GettingStartedCard", () => {
  it("shows steps", () => {
    const steps = [
      { id: "s1", title: "Create API Key", description: "Generate key", completed: true, codeSnippet: "" },
      { id: "s2", title: "First Request", description: "Call the API", completed: false, codeSnippet: "curl ..." },
    ];
    const { container } = render(<Card steps={steps} progressPct={50} done={false} nextStepId="s2" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Create API Key");
    expect(container.textContent).toContain("First Request");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Call the API");
  });
  it("shows completed", () => {
    const steps = [{ id: "s1", title: "Done", description: "", completed: true, codeSnippet: "" }];
    const { container } = render(<Card steps={steps} progressPct={100} done={true} nextStepId={null} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("All set!");
    expect(container.textContent).toContain("100%");
  });
});
