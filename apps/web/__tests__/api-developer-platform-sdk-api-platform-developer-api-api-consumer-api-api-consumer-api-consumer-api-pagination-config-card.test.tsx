import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-pagination-config-card";

describe("ConsumerApiPaginationConfigCard", () => {
  it("shows config", () => {
    const { container } = render(<Card consumerId="c1" defaultSize={20} maxSize={100} strategy="cursor" cursorParam="cursor" appName="App" />);
    expect(container.textContent).toContain("Pagination Config");
    expect(container.textContent).toContain("cursor");
    expect(container.textContent).toContain("20");
    expect(container.textContent).toContain("100");
  });
  it("shows offset strategy", () => {
    const { container } = render(<Card consumerId="c1" defaultSize={50} maxSize={200} strategy="offset" cursorParam="page" appName="App" />);
    expect(container.textContent).toContain("offset");
  });
});
