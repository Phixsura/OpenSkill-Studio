import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ContentStoreCard from "../src/components/content-store-card";

const items = [
  {
    key: "readme.md",
    content_type: "text/markdown",
    size_bytes: 2048,
    version: 3,
    updated_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    key: "config.json",
    content_type: "application/json",
    size_bytes: 512,
    version: 1,
    updated_at: new Date(Date.now() - 60000).toISOString(),
  },
];

describe("ContentStoreCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <ContentStoreCard
        items={items}
        appName="My App"
        totalSizeBytes={2560}
        maxSizeBytes={10485760}
      />,
    );
    expect(container.textContent).toContain("Content Store");
    expect(container.textContent).toContain("My App");
  });

  it("shows item count", () => {
    const { container } = render(
      <ContentStoreCard items={items} appName="App" totalSizeBytes={0} maxSizeBytes={1000} />,
    );
    expect(container.textContent).toContain("2 items");
  });

  it("shows storage usage", () => {
    const { container } = render(
      <ContentStoreCard
        items={items}
        appName="App"
        totalSizeBytes={5242880}
        maxSizeBytes={10485760}
      />,
    );
    expect(container.textContent).toContain("5.0 MB");
    expect(container.textContent).toContain("10.0 MB");
  });

  it("renders keys and content types", () => {
    const { container } = render(
      <ContentStoreCard items={items} appName="App" totalSizeBytes={0} maxSizeBytes={1000} />,
    );
    expect(container.textContent).toContain("readme.md");
    expect(container.textContent).toContain("text/markdown");
    expect(container.textContent).toContain("config.json");
  });

  it("shows version numbers", () => {
    const { container } = render(
      <ContentStoreCard items={items} appName="App" totalSizeBytes={0} maxSizeBytes={1000} />,
    );
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("v1");
  });

  it("shows file sizes", () => {
    const { container } = render(
      <ContentStoreCard items={items} appName="App" totalSizeBytes={0} maxSizeBytes={1000} />,
    );
    expect(container.textContent).toContain("2.0 KB");
    expect(container.textContent).toContain("512 B");
  });

  it("shows empty state", () => {
    const { container } = render(
      <ContentStoreCard items={[]} appName="App" totalSizeBytes={0} maxSizeBytes={1000} />,
    );
    expect(container.textContent).toContain("No content stored");
  });
});
