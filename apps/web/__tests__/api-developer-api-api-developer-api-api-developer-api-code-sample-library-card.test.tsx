import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibraryCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-code-sample-library-card";

const samples = [{ sample_id: "s1", title: "List Users", language: "python", endpoint: "/api/users", views: 500, copies: 120 }];

describe("Card", () => {
  it("shows code samples", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibraryCard samples={samples} languageCounts={{ python: 5, javascript: 3 }} appName="App" />);
    expect(container.textContent).toContain("Code Samples");
    expect(container.textContent).toContain("python: 5");
    expect(container.textContent).toContain("List Users");
    expect(container.textContent).toContain("500 views");
    expect(container.textContent).toContain("120 copies");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibraryCard samples={[]} languageCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No code samples");
  });
});
