"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth } from "@/lib/api";

interface Profile {
  username: string;
  headline: string | null;
  bio: string | null;
  location: string | null;
  website_url: string | null;
}

export default function EditProfilePage() {
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["portfolio-profile"],
    queryFn: () => apiWithAuth<{ data: Profile }>("/portfolio/profile"),
  });

  const profile = data?.data;
  const [form, setForm] = useState<Record<string, string>>({});
  const [message, setMessage] = useState<string | null>(null);

  // Initialize form with existing profile data
  useEffect(() => {
    if (profile && Object.keys(form).length === 0) {
      setForm({
        headline: profile.headline ?? "",
        bio: profile.bio ?? "",
        location: profile.location ?? "",
        website_url: profile.website_url ?? "",
      });
    }
  }, [profile]); // eslint-disable-line react-hooks/exhaustive-deps

  const saveMutation = useMutation({
    mutationFn: () => {
      // Convert empty strings to null for optional URL fields
      const payload = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [k, v === "" ? null : v]),
      );
      return apiWithAuth("/portfolio/profile", {
        method: "PUT",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio-profile"] });
      setMessage("Profile saved.");
    },
  });

  if (isLoading) return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError || !profile) return <p className="text-[hsl(var(--destructive))]">Failed to load profile.</p>;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold">Edit Profile</h1>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Username</label>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">{profile.username}</p>
        </div>
        <div>
          <label htmlFor="headline" className="block text-sm font-medium">Headline</label>
          <Input
            id="headline"
            value={form.headline ?? profile.headline ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, headline: e.target.value }))}
            placeholder="AI Developer & Prompt Engineer"
            className="mt-1"
          />
        </div>
        <div>
          <label htmlFor="bio" className="block text-sm font-medium">Bio</label>
          <textarea
            id="bio"
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            rows={5}
            value={form.bio ?? profile.bio ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))}
          />
        </div>
        <div>
          <label htmlFor="location" className="block text-sm font-medium">Location</label>
          <Input
            id="location"
            value={form.location ?? profile.location ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
            className="mt-1"
          />
        </div>
        <div>
          <label htmlFor="website" className="block text-sm font-medium">Website</label>
          <Input
            id="website"
            value={form.website_url ?? profile.website_url ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, website_url: e.target.value }))}
            className="mt-1"
          />
        </div>

        {message && <p className="text-sm text-[hsl(var(--muted-foreground))]">{message}</p>}

        <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? "Saving..." : "Save Changes"}
        </Button>
      </div>
    </div>
  );
}
