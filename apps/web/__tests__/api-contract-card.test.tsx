import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIContractCard from "../src/components/api-contract-card";

const contracts = [
  {
    contract_id: "c1",
    method: "POST",
    path: "/api/items",
    request_field_count: 3,
    response_field_count: 2,
    violation_count: 5,
  },
  {
    contract_id: "c2",
    method: "GET",
    path: "/api/users",
    request_field_count: 0,
    response_field_count: 4,
    violation_count: 0,
  },
];

describe("APIContractCard", () => {
  it("renders header and violation count", () => {
    const { container } = render(<APIContractCard contracts={contracts} appName="App" />);
    expect(container.textContent).toContain("API Contracts");
    expect(container.textContent).toContain("5 violations");
  });

  it("shows method and path", () => {
    const { container } = render(<APIContractCard contracts={contracts} appName="App" />);
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/api/items");
  });

  it("shows field counts", () => {
    const { container } = render(<APIContractCard contracts={contracts} appName="App" />);
    expect(container.textContent).toContain("3 req");
    expect(container.textContent).toContain("2 resp fields");
  });

  it("shows empty state", () => {
    const { container } = render(<APIContractCard contracts={[]} appName="App" />);
    expect(container.textContent).toContain("No API contracts");
  });
});
