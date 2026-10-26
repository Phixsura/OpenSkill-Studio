import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContractTestPanel } from "@/components/contract-test-panel";

const mockContracts = [
  { id: "ct1", provider: "ext-a", consumer: "ext-b", endpoint: "/api/users",
    method: "GET", fieldCount: 3 },
];
const mockResults = [
  { contractId: "ct1", result: "fail" as const,
    violations: ["Missing required field: name"], warnings: ["Unexpected field: extra"] },
];
const mockCompat = { provider: "ext-a", consumer: "ext-b", contracts: 1, passed: 0, failed: 1, compatible: false };

describe("ContractTestPanel", () => {
  it("renders contracts", () => {
    const { container } = render(
      <ContractTestPanel contracts={mockContracts} results={[]} compatibility={null} />
    );
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("ext-a → ext-b");
  });

  it("shows compatibility status", () => {
    const { container } = render(
      <ContractTestPanel contracts={mockContracts} results={mockResults} compatibility={mockCompat} />
    );
    expect(container.textContent).toContain("Incompatible");
  });

  it("shows test results", () => {
    const { getByText, container } = render(
      <ContractTestPanel contracts={mockContracts} results={mockResults} compatibility={null} />
    );
    fireEvent.click(getByText("Results (1)"));
    expect(container.textContent).toContain("Missing required field");
    expect(container.textContent).toContain("Unexpected field");
  });

  it("calls onRunTest", () => {
    const onRun = vi.fn();
    const { getByText } = render(
      <ContractTestPanel contracts={mockContracts} results={[]} compatibility={null} onRunTest={onRun} />
    );
    fireEvent.click(getByText("Test"));
    expect(onRun).toHaveBeenCalledWith("ct1");
  });
});
