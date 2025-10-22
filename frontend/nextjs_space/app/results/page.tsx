
import ResultsDashboard from "@/components/results-dashboard";

export default function ResultsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Backtest Results</h1>
        <p className="text-muted-foreground">
          Analyze performance metrics and trading results from your backtests
        </p>
      </div>
      
      <ResultsDashboard />
    </div>
  );
}
