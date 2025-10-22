
import BacktestForm from "@/components/backtest-form";

export default function BacktestPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Strategy Backtesting</h1>
        <p className="text-muted-foreground">
          Test your trading strategies against historical market data
        </p>
      </div>
      
      <BacktestForm />
    </div>
  );
}
