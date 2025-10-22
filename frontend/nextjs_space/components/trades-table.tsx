
'use client';

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Trade } from "@/lib/types";

interface TradesTableProps {
  trades: Trade[];
}

export default function TradesTable({ trades }: TradesTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const tradesPerPage = 10;

  if (!trades?.length) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No trades executed during this backtest
      </div>
    );
  }

  const totalPages = Math.ceil((trades?.length || 0) / tradesPerPage);
  const startIndex = (currentPage - 1) * tradesPerPage;
  const endIndex = startIndex + tradesPerPage;
  const currentTrades = trades?.slice(startIndex, endIndex) || [];

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value || 0);
  };

  const formatPercentage = (value: number) => {
    return `${((value || 0) * 100).toFixed(2)}%`;
  };

  return (
    <div className="space-y-4">
      <Table>
        <TableCaption>
          Showing {startIndex + 1}-{Math.min(endIndex, trades?.length || 0)} of {trades?.length || 0} trades
        </TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Type</TableHead>
            <TableHead>Entry Date</TableHead>
            <TableHead>Exit Date</TableHead>
            <TableHead className="text-right">Entry Price</TableHead>
            <TableHead className="text-right">Exit Price</TableHead>
            <TableHead className="text-right">Quantity</TableHead>
            <TableHead className="text-right">P&L</TableHead>
            <TableHead className="text-right">Return %</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {currentTrades?.map((trade) => {
            const isProfit = (trade?.profit_loss || 0) > 0;
            return (
              <TableRow key={trade?.id}>
                <TableCell>
                  <Badge variant={trade?.type === 'buy' ? 'default' : 'secondary'}>
                    {trade?.type?.toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell>
                  {new Date(trade?.entry_date || '').toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {new Date(trade?.exit_date || '').toLocaleDateString()}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(trade?.entry_price || 0)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(trade?.exit_price || 0)}
                </TableCell>
                <TableCell className="text-right">
                  {trade?.quantity || 0}
                </TableCell>
                <TableCell className={`text-right font-medium ${
                  isProfit ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(trade?.profit_loss || 0)}
                </TableCell>
                <TableCell className={`text-right font-medium ${
                  isProfit ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatPercentage(trade?.profit_loss_percentage || 0)}
                </TableCell>
              </TableRow>
            );
          }) ?? []}
        </TableBody>
      </Table>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
