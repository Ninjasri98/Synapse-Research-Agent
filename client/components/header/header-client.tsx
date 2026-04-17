"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { LogOut, Menu, User } from "lucide-react";
import { authClient } from "@/lib/auth-client";
import { toast } from "sonner";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { DonationButton } from "@/components/ui/donation-button";

export function HeaderClient() {
  const router = useRouter();
  const { data: session } = authClient.useSession();

  const handleSignOut = async () => {
    try {
      const { error } = await authClient.signOut();
      if (error) {
        toast.error("Failed to sign out");
        return;
      }
      router.push("/auth");
      router.refresh();
    } catch {
      toast.error("Failed to sign out");
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-14 items-center justify-between">
          <Link
            href="/"
            className="flex items-center space-x-2"
            data-umami-event="frontend_logo_click"
            data-umami-event-section="header"
          >
            <span className="font-bold text-xl">Synapse</span>
          </Link>

          <nav className="flex items-center gap-4">
            {session?.user ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-sm font-medium transition-colors hover:text-primary hidden sm:block"
                  data-umami-event="frontend_dashboard_nav_click"
                  data-umami-event-section="header"
                >
                  Dashboard
                </Link>
                <DonationButton
                  variant="outline"
                  size="sm"
                  className="hidden sm:flex"
                />
                <div className="hidden sm:flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    {session.user.name || session.user.email}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-sm font-medium hidden sm:flex"
                  onClick={handleSignOut}
                  data-umami-event="frontend_sign_out_click"
                  data-umami-event-section="header"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign out
                </Button>
                <Sheet>
                  <SheetTrigger asChild>
                    <Button variant="ghost" size="icon" className="sm:hidden">
                      <Menu className="h-6 w-6" />
                    </Button>
                  </SheetTrigger>
                  <SheetContent
                    side="left"
                    className="w-64 max-w-xs p-6 bg-background shadow-lg"
                  >
                    <SheetHeader>
                      <SheetTitle className="text-lg font-bold">
                        Menu
                      </SheetTitle>
                    </SheetHeader>
                    <div className="flex flex-col gap-6 mt-6">
                      <Link
                        href="/dashboard"
                        className="flex items-center gap-3 text-base font-medium transition-colors hover:text-primary"
                        data-umami-event="frontend_dashboard_nav_click"
                        data-umami-event-section="mobile_menu"
                      >
                        Dashboard
                      </Link>
                      <DonationButton
                        variant="outline"
                        size="lg"
                        className="justify-start"
                      />
                      <div className="flex items-center gap-3 text-base text-muted-foreground">
                        <User className="h-5 w-5" />
                        <span>{session.user.name || session.user.email}</span>
                      </div>
                      <div className="border-t border-muted my-2" />
                      <Button
                        variant="ghost"
                        size="lg"
                        className="flex items-center gap-3 text-base font-medium justify-start px-0"
                        onClick={handleSignOut}
                        data-umami-event="frontend_sign_out_click"
                        data-umami-event-section="mobile_menu"
                      >
                        <LogOut className="h-5 w-5" />
                        Sign out
                      </Button>
                    </div>
                  </SheetContent>
                </Sheet>
              </>
            ) : (
              <>
                <DonationButton
                  variant="outline"
                  size="sm"
                  className="hidden sm:flex"
                />
                <Button asChild>
                  <Link
                    href="/auth"
                    data-umami-event="frontend_get_started_click"
                    data-umami-event-section="header"
                  >
                    Get Started
                  </Link>
                </Button>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
