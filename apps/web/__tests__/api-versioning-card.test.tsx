import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIVersioningCard from "../src/components/api-versioning-card";

const versions = [
  { version: "v3", status: "active" as const, endpoint_count: 25 },
  { version: "v2", status: "deprecated" as const, endpoint_count: 20 },
  { version: "v1", status: "sunset" as const, endpoint_count: 15 },
];

describe("APIVersioningCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<APIVersioningCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("1 active / 3 total");
  });

  it("shows versions with status", () => {
    const { container } = render(<APIVersioningCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("deprecated");
    expect(container.textContent).toContain("sunset");
  });

  it("shows endpoint counts", () => {
    const { container } = render(<APIVersioningCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("25 endpoints");
  });

  it("shows empty state", () => {
    const { container } = render(<APIVersioningCard versions={[]} appName="App" />);
    expect(container.textContent).toContain("No API versions");
  });
});
