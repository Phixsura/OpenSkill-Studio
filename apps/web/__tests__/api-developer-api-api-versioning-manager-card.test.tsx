import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiVersioningManagerCard from "../src/components/api-developer-api-api-versioning-manager-card";

const versions = [
  { version: "v2", status: "active", endpoints_count: 25, traffic_pct: 80 },
  { version: "v1", status: "deprecated", endpoints_count: 20, traffic_pct: 20 },
];

describe("APIDeveloperAPIApiVersioningManagerCard", () => {
  it("shows versions", () => {
    const { container } = render(<APIDeveloperAPIApiVersioningManagerCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("API Versioning");
    expect(container.textContent).toContain("2 versions");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("80% traffic");
    expect(container.textContent).toContain("deprecated");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiVersioningManagerCard versions={[]} appName="App" />);
    expect(container.textContent).toContain("No API versions");
  });
});
