import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIClientRegistryCard from "../src/components/api-client-registry-card";

const clients = [
  { client_id: "c1", name: "Mobile App", status: "active" as const, request_count: 5000 },
  { client_id: "c2", name: "Legacy Bot", status: "suspended" as const, request_count: 100 },
];

describe("APIClientRegistryCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<APIClientRegistryCard clients={clients} appName="App" />);
    expect(container.textContent).toContain("API Clients");
    expect(container.textContent).toContain("1/2 active");
  });

  it("shows client names and status", () => {
    const { container } = render(<APIClientRegistryCard clients={clients} appName="App" />);
    expect(container.textContent).toContain("Mobile App");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("suspended");
  });

  it("shows request counts", () => {
    const { container } = render(<APIClientRegistryCard clients={clients} appName="App" />);
    expect(container.textContent).toContain("5000 reqs");
  });

  it("shows empty state", () => {
    const { container } = render(<APIClientRegistryCard clients={[]} appName="App" />);
    expect(container.textContent).toContain("No registered clients");
  });
});
