import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APICORSOriginLogCard from "../src/components/api-cors-origin-log-card";

const origins = [
  { origin: "https://app.example.com", request_count: 500, block_rate: 0, blocked_count: 0 },
  { origin: "https://evil.com", request_count: 10, block_rate: 100, blocked_count: 10 },
];

describe("APICORSOriginLogCard", () => {
  it("renders header and blocked count", () => {
    const { container } = render(<APICORSOriginLogCard origins={origins} uniqueCount={2} appName="App" />);
    expect(container.textContent).toContain("CORS Origins");
    expect(container.textContent).toContain("1 blocked");
  });

  it("shows origins and stats", () => {
    const { container } = render(<APICORSOriginLogCard origins={origins} uniqueCount={2} appName="App" />);
    expect(container.textContent).toContain("app.example.com");
    expect(container.textContent).toContain("500 reqs");
    expect(container.textContent).toContain("100% blocked");
  });

  it("shows empty state", () => {
    const { container } = render(<APICORSOriginLogCard origins={[]} uniqueCount={0} appName="App" />);
    expect(container.textContent).toContain("No CORS origins tracked");
  });
});
