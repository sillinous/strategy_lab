
import StrategyForm from "@/components/strategy-form";
import { strategyApi } from "@/lib/api";
import { notFound } from "next/navigation";

interface EditStrategyPageProps {
  params: {
    id: string;
  };
}

export default async function EditStrategyPage({ params }: EditStrategyPageProps) {
  const strategy = await strategyApi.getById(params?.id || "");
  
  if (!strategy) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Edit Strategy</h1>
        <p className="text-muted-foreground">
          Modify your trading strategy configuration
        </p>
      </div>
      
      <StrategyForm strategy={strategy} />
    </div>
  );
}
