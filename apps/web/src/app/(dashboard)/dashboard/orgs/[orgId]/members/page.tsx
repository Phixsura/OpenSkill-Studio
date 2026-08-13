"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth } from "@/lib/api";

interface MemberUser {
  id: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
}

interface OrgMember {
  id: string;
  user: MemberUser;
  role: string;
  status: string;
  joined_at: string;
}

export default function MembersPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const [showInvite, setShowInvite] = useState(false);
  const [inviteRole, setInviteRole] = useState("student");
  const [inviteLink, setInviteLink] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["org-members", orgId],
    queryFn: () =>
      apiWithAuth<{ data: OrgMember[]; meta: { total: number } }>(
        `/orgs/${orgId}/members`,
      ),
  });

  const inviteMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { code: string } }>(`/orgs/${orgId}/invite-links`, {
        method: "POST",
        body: JSON.stringify({ role: inviteRole, max_uses: 10 }),
      }),
    onSuccess: (result) => {
      const code = result.data.code;
      setInviteLink(`${window.location.origin}/join/${code}`);
      queryClient.invalidateQueries({ queryKey: ["org-members", orgId] });
    },
  });

  const members = data?.data ?? [];
  const total = data?.meta?.total ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Members</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            {isLoading ? "Loading members..." : `${total} member${total !== 1 ? "s" : ""}`}
          </p>
        </div>
        <Button onClick={() => setShowInvite(!showInvite)}>Invite</Button>
      </div>

      {showInvite && (
        <div className="rounded-lg border p-4 space-y-3">
          <h3 className="font-medium">Create Invite Link</h3>
          <div className="flex items-center gap-3">
            <label className="text-sm">Role:</label>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="rounded border px-2 py-1 text-sm"
            >
              <option value="student">Student</option>
              <option value="instructor">Instructor</option>
              <option value="admin">Admin</option>
            </select>
            <Button
              size="sm"
              onClick={() => inviteMutation.mutate()}
              disabled={inviteMutation.isPending}
            >
              {inviteMutation.isPending ? "Creating..." : "Generate Link"}
            </Button>
          </div>
          {inviteLink && (
            <div className="flex items-center gap-2">
              <Input value={inviteLink} readOnly className="font-mono text-xs" />
              <Button
                size="sm"
                variant="secondary"
                onClick={() => navigator.clipboard.writeText(inviteLink)}
              >
                Copy
              </Button>
            </div>
          )}
        </div>
      )}

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-[hsl(var(--secondary))]">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Name</th>
              <th className="px-4 py-3 text-left font-medium">Email</th>
              <th className="px-4 py-3 text-left font-medium">Role</th>
              <th className="px-4 py-3 text-left font-medium">Joined</th>
            </tr>
          </thead>
          <tbody>
            {members.map((m) => (
              <tr key={m.id} className="border-t">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[hsl(var(--primary))] text-xs font-medium text-[hsl(var(--primary-foreground))]">
                      {m.user.display_name.charAt(0).toUpperCase()}
                    </div>
                    {m.user.display_name}
                  </div>
                </td>
                <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                  {m.user.email}
                </td>
                <td className="px-4 py-3">
                  <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs capitalize">
                    {m.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                  {new Date(m.joined_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
