import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { NotebookPolling } from "@/components/notebook/notebook-polling";
import { NotebookWithDetails } from "@/lib/notebook-types";

async function getNotebook(id: string, userId: string) {
  return prisma.notebook.findUnique({
    where: {
      id,
      userId,
    },
    include: {
      processingStatus: true,
      sources: true,
      output: {
        include: {
          faqs: true,
        },
      },
    },
  });
}

export default async function NotebookPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/auth");
  }

  const notebook = await getNotebook(id, session.user.id);

  if (!notebook) {
    redirect("/dashboard");
  }

  // Type assertion to match the expected type
  return (
    <NotebookPolling
      initialNotebook={notebook as unknown as NotebookWithDetails}
    />
  );
}
