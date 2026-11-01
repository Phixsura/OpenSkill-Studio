import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResourceLockCard from "../src/components/resource-lock-card";

const locks = [
  {
    resource: "orders/123",
    owner: "worker-1",
    acquired_at: new Date(Date.now() - 10_000).toISOString(),
    expires_in_seconds: 20,
  },
  {
    resource: "users/456",
    owner: "api-service",
    acquired_at: new Date(Date.now() - 5_000).toISOString(),
    expires_in_seconds: 25,
  },
];

describe("ResourceLockCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ResourceLockCard locks={locks} appName="My App" />);
    expect(container.textContent).toContain("Resource Locks");
    expect(container.textContent).toContain("My App");
  });

  it("shows active lock count", () => {
    const { container } = render(<ResourceLockCard locks={locks} appName="App" />);
    expect(container.textContent).toContain("2 active");
  });

  it("shows none-held when empty", () => {
    const { container } = render(<ResourceLockCard locks={[]} appName="App" />);
    expect(container.textContent).toContain("None held");
    expect(container.textContent).toContain("No active locks");
  });

  it("renders resource names with lock icon", () => {
    const { container } = render(<ResourceLockCard locks={locks} appName="App" />);
    expect(container.textContent).toContain("🔒 orders/123");
    expect(container.textContent).toContain("🔒 users/456");
  });

  it("shows owner", () => {
    const { container } = render(<ResourceLockCard locks={locks} appName="App" />);
    expect(container.textContent).toContain("worker-1");
    expect(container.textContent).toContain("api-service");
  });

  it("shows expiry countdown", () => {
    const { container } = render(<ResourceLockCard locks={locks} appName="App" />);
    expect(container.textContent).toContain("expires in 20s");
  });
});
