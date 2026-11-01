import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIVersionRouterCard from "../src/components/api-version-router-card";

const versions = [
  {
    version: "v3",
    status: "active" as const,
    base_path: "/api/v3",
    is_default: true,
    sunset_date: "",
  },
  {
    version: "v2",
    status: "deprecated" as const,
    base_path: "/api/v2",
    is_default: false,
    sunset_date: "2027-06-01",
  },
  {
    version: "v1",
    status: "sunset" as const,
    base_path: "/api/v1",
    is_default: false,
    sunset_date: "2026-01-01",
  },
];

describe("APIVersionRouterCard", () => {
  it("renders header", () => {
    const { container } = render(<APIVersionRouterCard versions={versions} appName="My App" />);
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(<APIVersionRouterCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("1 active");
  });

  it("renders versions and paths", () => {
    const { container } = render(<APIVersionRouterCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("/api/v3");
    expect(container.textContent).toContain("v1");
  });

  it("shows status badges", () => {
    const { container } = render(<APIVersionRouterCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("deprecated");
    expect(container.textContent).toContain("sunset");
  });

  it("shows default label", () => {
    const { container } = render(<APIVersionRouterCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("default");
  });

  it("shows sunset date", () => {
    const { container } = render(<APIVersionRouterCard versions={versions} appName="App" />);
    expect(container.textContent).toContain("sunset 2027-06-01");
  });

  it("shows empty state", () => {
    const { container } = render(<APIVersionRouterCard versions={[]} appName="App" />);
    expect(container.textContent).toContain("No API versions");
  });
});
