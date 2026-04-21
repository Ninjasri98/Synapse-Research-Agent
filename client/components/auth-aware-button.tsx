"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";

export function AuthAwareButton() {
  const router = useRouter();

  const handleGetStarted = async () => {
    try {
      const { data: session, error } = await authClient.getSession();

      if (error || !session) {
        // User is not authenticated, go to auth page
        router.push("/auth");
        return;
      }

      // User is already authenticated, go to dashboard
      router.push("/dashboard");
    } catch (error) {
      console.error("Error checking authentication status:", error);
      // Default to auth page if there's an error
      router.push("/auth");
    }
  };

  return (
    <Button
      size="lg"
      onClick={handleGetStarted}
      data-umami-event="frontend_get_started_click"
      data-umami-event-section="hero"
    >
      Get Started
    </Button>
  );
}
