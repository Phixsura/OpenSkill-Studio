import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperCodeSampleCard from "../src/components/api-developer-code-sample-card";

const samples = [
  { sample_id: "s1", endpoint: "GET /api/users", language: "python", title: "List Users", copy_count: 42 },
  { sample_id: "s2", endpoint: "POST /api/apps", language: "javascript", title: "Create App", copy_count: 15 },
];

describe("APIDeveloperCodeSampleCard", () => {
  it("shows samples", () => {
    const { container } = render(<APIDeveloperCodeSampleCard samples={samples} appName="App" />);
    expect(container.textContent).toContain("Code Samples");
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("List Users");
    expect(container.textContent).toContain("42 copies");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperCodeSampleCard samples={[]} appName="App" />);
    expect(container.textContent).toContain("No code samples");
  });
});
