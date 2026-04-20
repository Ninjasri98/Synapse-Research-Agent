import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { NotebookList } from "@/components/notebook/notebook-list";

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/auth");
  }

  const notebooks = await prisma.notebook.findMany({
    where: {
      userId: session.user.id,
    },
    include: {
      processingStatus: true,
      sources: true,
    },
    orderBy: {
      createdAt: "desc",
    },
  });

  return (
    <div className="container mx-auto px-4 py-2 sm:py-4">
      <div className="max-w-7xl mx-auto">
        <NotebookList notebooks={notebooks} />
      </div>
    </div>
  );
}
