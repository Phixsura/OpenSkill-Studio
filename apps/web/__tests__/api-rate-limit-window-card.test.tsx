import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIRateLimitWindowCard from "../src/components/api-rate-limit-window-card";

const windows = [
  { consumer_id: "app-1", usage: 80, max_requests: 100, remaining: 20 },
  { consumer_id: "app-2", usage: 100, max_requests: 100, remaining: 0 },
];

describe("APIRateLimitWindowCard", () => {
  it("renders header and window info", () => {
    const { container } = render(<APIRateLimitWindowCard windows={windows} windowSeconds={60} appName="App" />);
    expect(container.textContent).toContain("Rate Windows");
    expect(container.textContent).toContain("60s window");
    expect(container.textContent).toContain("2 consumers");
  });

  it("shows usage bars", () => {
    const { container } = render(<APIRateLimitWindowCard windows={windows} windowSeconds={60} appName="App" />);
    expect(container.textContent).toContain("app-1");
    expect(container.textContent).toContain("80/100");
  });

  it("shows empty state", () => {
    const { container } = render(<APIRateLimitWindowCard windows={[]} windowSeconds={60} appName="App" />);
    expect(container.textContent).toContain("No active windows");
  });
});
