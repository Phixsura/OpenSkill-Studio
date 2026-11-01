import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeployLockCard from "../src/components/deploy-lock-card";

const activeLock = {
  lock_id: "l1",
  owner: "alice",
  reason: "v2.0 deploy",
  is_active: true,
  is_expired: false,
};
const history = [
  { lock_id: "l0", owner: "bob", reason: "", is_active: false, is_expired: false },
  { lock_id: "l1", owner: "alice", reason: "v2.0", is_active: true, is_expired: false },
];

describe("DeployLockCard", () => {
  it("shows locked state", () => {
    const { container } = render(
      <DeployLockCard currentLock={activeLock} history={history} appName="App" />,
    );
    expect(container.textContent).toContain("Locked");
    expect(container.textContent).toContain("Locked by alice");
  });

  it("shows unlock state", () => {
    const { container } = render(<DeployLockCard currentLock={null} history={[]} appName="App" />);
    expect(container.textContent).toContain("Unlocked");
  });

  it("shows reason", () => {
    const { container } = render(
      <DeployLockCard currentLock={activeLock} history={[]} appName="App" />,
    );
    expect(container.textContent).toContain("v2.0 deploy");
  });

  it("shows history", () => {
    const { container } = render(
      <DeployLockCard currentLock={null} history={history} appName="App" />,
    );
    expect(container.textContent).toContain("Recent locks");
    expect(container.textContent).toContain("bob");
  });

  it("shows empty state", () => {
    const { container } = render(<DeployLockCard currentLock={null} history={[]} appName="App" />);
    expect(container.textContent).toContain("No deploy locks");
  });
});
