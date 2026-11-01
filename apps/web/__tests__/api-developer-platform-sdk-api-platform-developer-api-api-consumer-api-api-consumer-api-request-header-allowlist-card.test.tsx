import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-header-allowlist-card";

describe("RequestHeaderAllowlistCard", () => {
  it("shows allowlists", () => {
    const allowlists = [{ consumer_id: "c1", allowed_count: 5, strip_unknown: true }];
    const { container } = render(<Card allowlists={allowlists} appName="App" />);
    expect(container.textContent).toContain("Header Allowlist");
    expect(container.textContent).toContain("5 allowed");
    expect(container.textContent).toContain("strip");
  });
  it("shows empty", () => {
    const { container } = render(<Card allowlists={[]} appName="App" />);
    expect(container.textContent).toContain("No header allowlists");
  });
});
