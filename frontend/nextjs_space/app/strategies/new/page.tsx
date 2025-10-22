
import StrategyForm from "@/components/strategy-form";

export default function NewStrategyPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Strategy Builder</h1>
        <p className="text-muted-foreground">
          Create a new trading strategy with custom indicators and conditions
        </p>
      </div>
      
      <StrategyForm />
    </div>
  );
}
